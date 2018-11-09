from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, FieldList
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, Length
import json

with open("credentials.json", "r") as f:
    creds = json.load(f)
    institutes = [(thing, thing) for thing in creds['emails'].keys()]

class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email address.")])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=16, message="Password must be 8-16 characters.")])
    submit = SubmitField("Login")

class AddSampleForm(Form):
    patientNumber =StringField("Patient Number.")
    filterNumber = FieldList(StringField("Filter Number."), min_entries=1)
    dateRec = DateField("Date Received.", format='%Y-%m-%d')
    mLBlood = FloatField("Millilitres of blood in tube.")
    initials = StringField("Initials of sender.")
    institute = SelectField("Institute of Origin", choices = institutes)
    submit = SubmitField("Submit")