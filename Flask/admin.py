from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, request
from Classes.models import db, User


class AdminView(ModelView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.static_folder = 'static'

    def is_accessible(self):
        currUser = User.query.filter_by(id=session.get('user_id')).first()
        return currUser.email == 'lando.wark@gmail.com'

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home', next=request.url))
