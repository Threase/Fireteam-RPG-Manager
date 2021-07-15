from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, AnyOf
from fireteam_manager.models import User


class RegisterNewUser(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Is Admin User?', default=False, validators=[AnyOf([True, False])])
    is_super_admin = BooleanField('Is Super Admin User?', default=False, validators=[AnyOf([True, False])])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username already exists, do they already have an account?')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already attached to an account? '
                                  'Does this user already have an account?')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Login')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update Information')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account with this email already exists.')


class UpdateUserForm(FlaskForm):
    selected_user_to_edit = User()
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Give Admin rights?', default=False, validators=[AnyOf([True, False])])
    is_super_admin = BooleanField('Give Super Admin rights?', default=False, validators=[AnyOf([True, False])])
    submit = SubmitField('Edit User')

    def validate_username(self, username):
        if username.data != self.selected_user_to_edit.username:
            new_username = User.query.filter_by(username=username.data).first()
            if new_username:
                raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        if email.data != self.selected_user_to_edit.email:
            new_email = User.query.filter_by(email=email.data).first()
            if new_email:
                raise ValidationError('This email is already taken.')


# TODO: Finish implementing
class CreateGameForm(FlaskForm):
    title = StringField('Name of Game', validators=[DataRequired(), Length(min=2, max=100)])