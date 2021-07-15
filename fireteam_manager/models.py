import os
import json
from datetime import datetime
from fireteam_manager import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_super_admin = db.Column(db.Boolean, nullable=False, default=True)
    has_changed_password = db.Column(db.Boolean, nullable=False, default=False)
    characters = db.relationship('Character', backref='owner', lazy=True)
    games = db.relationship('Game', backref='player', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    character_name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_npc = db.Column(db.Boolean, nullable=False, default=True)
    character_level = db.Column(db.Integer, nullable=False, default=0)
    # Following two lines are a dictionary, keys are the name of the stat, the values are ints.
    character_primary_stats_json = db.Column(db.String(100))
    character_secondary_stats_json = db.Column(db.String(100))

    def __repr__(self):
        return f"Character('{self.character_name}', owned by '{self.user_id}')"


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text())
    date_create = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)




if os.path.exists('site.db') is False:  # Create the .db in case it had to be deleted for some reason.
    db.create_all()
