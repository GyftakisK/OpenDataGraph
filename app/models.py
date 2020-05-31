from time import time
from datetime import datetime
import jwt
from app import db, login, celery
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean)

    def __init__(self, username, email, is_admin=False):
        super(User, self).__init__()
        self.username = username
        self.email = email
        self.is_admin = is_admin

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            _id = jwt.decode(token, current_app.config['SECRET_KEY'],
                             algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(_id)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), index=True, unique=True)
    task_name = db.Column(db.String(30))
    task_inputs = db.Column(db.String(200))
    creator = db.Column(db.Integer)
    status = db.Column(db.String(12))
    added_on = db.Column(db.DATETIME)

    def __init__(self, task_id, task_name, task_inputs, user_id):
        super(Task, self).__init__()
        self.task_id = task_id
        self.task_name = task_name
        self.task_inputs = task_inputs
        self.creator = user_id
        self.status = ""
        self.added_on = datetime.utcnow()

    def __repr__(self):
        return '<Task {} Status: {}>'.format(self.task_id, self.status)

    def get_status(self) -> str:
        if not self.status or self.status not in ['SUCCESS', 'FAILURE']:
            self.status = celery.AsyncResult(self.task_id).state
            db.session.commit()
        return self.status

    def get_creator_email(self) -> str:
        return User.query.get(self.creator).email
