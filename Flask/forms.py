from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email address.")])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=16, message="Password must be 8-16 characters.")])
    submit = SubmitField("Login")