from Classes.models import User
from random import *
import string
import sqlite3
import os
from getpass import getpass

def generate_apikey():
    return ''.join(choice(string.hexdigits) for x in range(8))


def input_data():
    pass_match = False
    user = input("Input user name: [Landon] \n") or "Landon"
    email = input("Input user's email: [lando.wark@gmail.com] \n") or "lando.wark@gmail.com"
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
    apikey = generate_apikey()
    print("This user's apikey is {}. Write it down because it's about to get hashed to shit.".format(apikey))
    newUser = User(name=user, email=email, password=password1, apikey=apikey)
    return newUser

if __name__ == "__main__":
    newUser = input_data()
    sql = '''INSERT INTO users(name,email,password,apikey) VALUES(?,?,?,?)'''
    databaseLoc = os.path.abspath(os.path.relpath("DB_DIR/database.sqlite", os.path.abspath(__file__)))
    conn = sqlite3.connect(databaseLoc)
    cursor = conn.cursor()
    cursor.execute(sql, (newUser.name, newUser.email, newUser.pwdhash, newUser.apihash))
    conn.commit()
    conn.close()
