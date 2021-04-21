#!/var/www/precise/venv/bin/python3

import sys
import os
from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password
from getpass import getpass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Flask.routes import app
from Classes.models import User, db, Role

default_email = "lando.wark@gmail.com"

def input_data():
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    pass_match = False
    email = input("Input user's email: [{}] \n".format(default_email)) or default_email
    while pass_match == False:
        password1 = getpass(prompt="Input user password [8-16 chars]: \n")
        password2 = getpass(prompt="Repeat user password: \n")
        if len(password1) > 8 and len(password1) < 16 and password1 == password2:
            print("Password accepted")
            pass_match = True
        elif len(password1) < 8:
            print("Password is too short!")
        elif len(password1) > 16:
            print("Password is too long!")
        elif password1 != password2:
            print("Passwords don't match!")
        else:
            print("Something went wrong.")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        user_datastore.create_user(email=email, password=hash_password(password1))
        db.session.commit()

if __name__ == "__main__":
    input_data()