import os

DB_PATH = os.path.abspath(os.path.relpath("db.sqlite3"))
SECRET_KEY = 'development key' # keep this key secret during production
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(DB_PATH)
SQLALCHEMY_TRACK_MODIFICATIONS = False
JWT_SECRET_KEY = 'jwt-secret-string'
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16MB
STATIC_FOLDER = os.path.abspath(os.path.relpath("Flask/static"))
SECURITY_URL_PREFIX = "/precise"
# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = "/login/"
SECURITY_LOGOUT_URL = "/logout/"
SECURITY_PASSWORD_SALT = "You are watching me type"
SECURITY_POST_LOGIN_VIEW = "/precise/addsample"
SECURITY_POST_LOGOUT_VIEW = "/precise/login"
# Flask-Security features
SECURITY_REGISTERABLE = False
SECURITY_SEND_REGISTER_EMAIL = False
DEBUG = True
