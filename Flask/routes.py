from bokeh.embed import components
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_security import SQLAlchemyUserDatastore, Security, login_required

from Flask.admin import AdminView
from Flask.resources import filter, logon, TokenRefresh
from Flask.forms import LoginForm, AddSampleForm
from Flask import config
from Classes.models import User, db, Role
from AddData.sample_adder import add
import os
from ChartMakers.bokeh_maker import create_hover_tool, create_histogram
from flask_jwt_extended import JWTManager
import datetime
import logging

app = Flask(__name__)
app.config.from_object(config)
print(app.config['STATIC_FOLDER'])
api = Api(app)
Bootstrap(app)
# Must be done before db.init
app.logger = logging.getLogger("Flask.routers")

jwt = JWTManager(app)
db.init_app(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = Admin(app, name='Dashboard', index_view=AdminView(User, db.session, url='/precise/admin', endpoint='admin'))
#admin.add_view(AdminView(User, db.session))

@app.before_first_request
def create():
    db.create_all()

@app.route("/precise")
def index():
    return redirect(url_for("login"))

@app.route("/precise/img/<string:patient_number>/<string:parameter_name>", methods=["GET"])
@login_required
def chart(patient_number, parameter_name):
    hover = create_hover_tool()
    title_string = parameter_name + " vs. PSA for " + patient_number
    plot = create_histogram(patient_number, parameter_name, title_string, "Dates",
                            parameter_name, hover)
    script, div = components(plot)
    return render_template("chart.html", parameter_name=parameter_name, patient_number=patient_number,
                           the_div=div, the_script=script)

@app.route("/precise/addsample", methods=["GET", "POST"])
@login_required
def addsample():
    form = AddSampleForm()
    if request.method == "POST":
        if form.validate == False:
            return render_template("addsample.html", form=form)
        else:
            user = User.query.filter_by(id=session.get('user_id')).first().email
            patientNumber = form.patientNumber.data
            filterNumber = form.filterNumber.data
            dateRec = datetime.datetime.strftime(form.dateRec.data, "%Y-%m-%d")
            mLBlood = form.mLBlood.data
            initials = form.initials.data
            add(patientNumber=patientNumber, filterNumber=filterNumber, dateRec=dateRec, mLBlood=mLBlood, initials=initials, receiver=user)
            flash("Sample {}, {} has been added".format(patientNumber, filterNumber))
            logging.info("{} has added sample {}, {}".format(user, patientNumber, filterNumber))
            return redirect(url_for("addsample"))
    elif request.method == "GET":
        return render_template("addsample.html", form=form)


api.add_resource(filter, "/precise/api")
api.add_resource(logon, "/precise/api/login")
api.add_resource(TokenRefresh, "/precise/api/tokenrefresh")
