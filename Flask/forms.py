from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, FieldList, FileField, HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, Length
from DB_DIR import mongo as mng
import json
import os

with open("credentials.json", "r") as f:
    creds = json.load(f)
    institutes = [(thing, thing) for thing in creds['emails'].keys()]
patients = [(pat, pat) for pat in sorted(mng.getPatientList())]



class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email address.")])
    password = PasswordField("Password",
                             validators=[DataRequired(), Length(min=8, max=16, message="Password must be 8-16 characters.")])
    submit = SubmitField("Login")


class AddSampleForm(Form):
    patientNumber = StringField("Patient Number.")
    filterNumber = FieldList(StringField("Filter Number."), min_entries=1)
    dateRec = DateField("Date Received.", format='%Y-%m-%d')
    mLBlood = FloatField("Millilitres of blood in tube.")
    initials = StringField("Initials of sender.")
    institute = SelectField("Institute of Origin", choices = institutes)
    submit = SubmitField("Submit")


class UploadForm(Form):
    upfile = FileField("Upload", validators=None) # none for now
    notInJSON = {}
    submit = SubmitField("Upload")


class CorrectionsForm(Form):
    orphans = FieldList(SelectField(None, choices=[], default='', coerce=str))
    submit = SubmitField("Submit")


class UploadZipForm(Form):
    patientNumber = SelectField("Patient Number.", choices = patients)
    filterNumber = StringField("Filter Number.")
    upfile = FileField("Upload", validators=None)  # none for now
    submit = SubmitField("Upload")

