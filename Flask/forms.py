from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, Length

institutes = ["Mai Lab", "London Health Sciences Centre", "Sunnybrook", "ScreenCell", "Vancouver Prostate Centre"]

class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email address.")])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=16, message="Password must be 8-16 characters.")])
    submit = SubmitField("Login")

class AddSampleForm(Form):
    patientNumber =StringField("Patient Number.")
    filterNumber = StringField("Filter Number.")
    dateRec = DateField("Date Received.", format='%Y-%m-%d')
    mLBlood = FloatField("Millilitres of blood in tube.")
    initials = StringField("Initials of sender.")
    institute = SelectField("Institute of Origin", choices = institutes, validators = [DataRequired()])
    submit = SubmitField("Submit")