import secrets
from PIL import Image
import os
from flask import render_template, url_for, flash, redirect, request, abort
from fireteam_manager import app, db, bcrypt
from fireteam_manager.forms import (RegisterNewUser, LoginForm, UpdateAccountForm, UpdateUserForm)
from fireteam_manager.models import User, Character, Game
from flask_login import login_user, current_user, logout_user, login_required

# Creates a test admin account in case i had to delete the .db in development
if app.debug is True:
    if not User.query.filter_by(username='testadmin').first():
        debug_admin = User()
        debug_admin.username = 'testadmin'
        debug_admin.password = bcrypt.generate_password_hash('password').decode('utf-8')
        debug_admin.email = 'admintestemail@email.com'
        debug_admin.is_admin = True
        debug_admin.is_super_admin = True
        db.session.add(debug_admin)
        db.session.commit()
        print("CREATED TEST SUPER ADMIN ACCOUNT")

# TODO: Create home page that actually does something
@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated and current_user.has_changed_password is False:
        flash('Please change your password in the account settings menu.', 'danger')
    return render_template('home.html')

# TODO: Create an about page. Maybe link to github once its posted?
@app.route('/about')
def about():
    return render_template('about.html', title='About')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if user.has_changed_password is False:
                flash('Please change your password.', 'warning')
                return redirect(url_for('account'))
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed, please check username and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register_new_user():
    if current_user.is_authenticated is False or current_user.is_admin is False:
        flash('You are not listed as an admin account. You cannot register new users.',
              'danger')
        return redirect(url_for('home'))
    form = RegisterNewUser()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.password = hashed_password
        user.is_admin = form.is_admin.data
        user.is_super_admin = form.is_super_admin.data
        if user.is_admin is False and user.is_super_admin is True:
            user.is_admin = True  # User must be admin to be super admin.
        db.session.add(user)
        db.session.commit()
        flash('The account for user: ' + user.username + ' has been created.', 'success')
    return render_template('register.html', form=form, title='Create New User')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def delete_old_picture(picture):  # Deletes old profile pic to prevent tons of storage issues.
    if picture == 'default.jpg':  # Dont delete default.jpg
        return
    else:
        try:
            os.remove(os.path.join(app.root_path, 'static', 'profile_pics', picture))
        except OSError:
            pass


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            delete_old_picture(current_user.image_file)
            current_user.image_file = picture_file
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.email = form.email.data
        current_user.has_changed_password = True
        db.session.commit()
        flash('Your account information has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

# TODO: Create
@app.route('/new_character')
@login_required
def new_character():
    return render_template('home.html')


# TODO: RECREATE GAMES.HTML BECAUSE FUCKING GIT DELETED IT WITHOUT ANY WAY TO GET IT BACK
# TODO: NEVER INTEGRATE GIT EVER AGAIN.
@app.route('/games')
@login_required
def games():
    list_of_all_games = Game.query.order_by(Game.id.asc()).all()
    print(list_of_all_games[0].title)
    list_of_all_characters = Character.query.order_by(Character.id.asc()).all()
    return render_template('games.html',
                           game_list=list_of_all_games,
                           character_list=list_of_all_characters,
                           title='Games')


@app.route('/manage_users')
@login_required
def manage_users():
    if current_user.is_admin is False:
        abort(403)
    list_of_all_users = User.query.order_by(User.id.asc()).all()
    return render_template('manage_users.html', title='Manage Users', users=list_of_all_users)


@app.route('/edit_user/<string:selected_user>', methods=['GET', 'POST'])
@login_required
def edit_user(selected_user):
    selected_user = User.query.get_or_404(selected_user)
    if current_user.is_admin is False:
        abort(403)
    if current_user.id == selected_user.id:
        flash('Use Account page to update own account information.', 'danger')
        return redirect(url_for('account'))
    form = UpdateUserForm()
    form.selected_user_to_edit = selected_user
    if form.validate_on_submit():
        selected_user.username = form.username.data
        selected_user.email = form.email.data
        selected_user.is_admin = form.is_admin.data
        selected_user.is_super_admin = form.is_super_admin.data
        db.session.add(selected_user)
        db.session.commit()
        flash('User has been updated.', 'success')
        redirect(url_for('edit_user', selected_user=selected_user.id))
    elif request.method == 'GET':
        form.email.data = selected_user.email
        form.username.data = selected_user.username
        form.is_admin.data = selected_user.is_admin
        form.is_super_admin.data = selected_user.is_super_admin
    return render_template('edit_user.html', form=form, title='Edit User', user=selected_user)


@app.route('/delete_account/<string:selected_account>', methods=['POST'])
@login_required
def delete_account(selected_account):
    selected_user = User.query.get_or_404(selected_account)
    if current_user.is_admin is False:
        abort(403)
    if selected_user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('home'))
    db.session.delete(selected_user)
    db.session.commit()
    flash('This account has been deleted.', 'info')
    return redirect(url_for('manage_users'))
