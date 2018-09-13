from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):

    __tab1ename__ = 'user'
    uid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))
    apikey = db.Column(db.String(54))

    def __init__(self, name,  email, password, apikey):
        self.name = name.title()
        self.email = email.lower()
        self.set_password(password)
        self.apikey = apikey

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()