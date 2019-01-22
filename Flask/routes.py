import os

from bokeh.embed import components
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask.json import jsonify
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_security import SQLAlchemyUserDatastore, Security, login_required
from werkzeug.utils import secure_filename
from wtforms import SelectField
from Flask.admin import AdminView
from Flask.resources import filter, ApiLogin, TokenRefresh, All_Patients, Janine_DidNot
from Flask.forms import AddSampleForm, UploadForm, CorrectionsForm, UploadZipForm
from Scripts import zip_parser
from Flask import config, email
from DB_DIR import mongo as mng
from Classes.models import User, db, Role
from AddData.sample_adder import add
from ChartMakers.bokeh_maker import create_hover_tool, create_histogram
from flask_jwt_extended import JWTManager
from AddData.janine_scraper import *
import datetime
import logging
import platform
import json


app = Flask(__name__)
app.config.from_object(config)
api = Api(app)
Bootstrap(app)
# Must be done before db.init
app.logger = logging.getLogger("Flask.routers")
device = platform.node()

jwt = JWTManager(app)
db.init_app(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = Admin(app, name='Dashboard', index_view=AdminView(User, db.session, url='/admin', endpoint='admin'))

@app.before_first_request
def create():
    db.create_all()



@app.route("/img/<string:patient_number>/<string:parameter_name>", methods=["GET"])
@login_required
def chart(patient_number, parameter_name):
    hover = create_hover_tool()
    title_string = parameter_name + " vs. PSA for " + patient_number
    plot = create_histogram(patient_number, parameter_name, title_string, "Dates",
                            parameter_name, hover)
    script, div = components(plot)
    return render_template("chart.html", parameter_name=parameter_name, patient_number=patient_number,
                           the_div=div, the_script=script)

@app.route("/addsample", methods=["GET", "POST"])
@app.route("/addsample/<int:num_filters>", methods=["GET", "POST"])
@login_required
def addsample(num_filters=1):
    form = AddSampleForm()
    for iii in range(1, num_filters):
        form.filterNumber.append_entry()
    if request.method == "POST":
        if form.validate == False:
            return render_template("addsample.html", form=form)
        else:
            user = User.query.filter_by(id=session.get('user_id')).first().email
            patientNumber = form.patientNumber.data
            filterNumbers = form.filterNumber.data
            dateRec = datetime.datetime.strftime(form.dateRec.data, "%Y-%m-%d")
            mLBlood = form.mLBlood.data
            initials = form.initials.data
            institute = form.institute.data
            for filterNumber in filterNumbers:
                if filterNumber != "":
                    already_seen = add(patientNumber=patientNumber, filterNumber=filterNumber, dateRec=dateRec, mLBlood=mLBlood, initials=initials, receiver=user, institute=institute)
                    if already_seen > 0:
                        app.logger.info("New sample. Sending email.")
                        if device != "landons-laptop":
                            email.sendemail(patientNumber, user, institute, already_seen)
                    flash("Sample {}, {} has been added".format(patientNumber, filterNumber))
                    app.logger.info("{} has added sample {}, {}".format(user, patientNumber, filterNumber))
            return redirect(url_for("addsample"))
    elif request.method == "GET":
        return render_template("addsample.html", form=form)

@app.route("/janinescrape", methods=["GET", "POST"])
@login_required
def janinescrape(ALLOWED_EXTENSIONS = ['.csv', '.xls', '.xlsx']):
    form = UploadForm()
    user = User.query.filter_by(id=session.get('user_id')).first().email
    if request.method == 'POST':
        if form.validate == False:
            return render_template("fileupload.html", form=form)
        app.logger.info("{} uploaded a Janine file.".format(user))
        f = request.files.getlist('upfile')
        file = f[0]
        if os.path.splitext(secure_filename(file.filename))[1] in ALLOWED_EXTENSIONS:
            newFile = uploadFile(file)
            # get dict of filters from file.
            filters = openFileAndParse(newFile)
            # split into two lists of dictionaries
            yesInDB, notInDB = makeLists(filters)
            for filter in yesInDB:
                #inDBData = [filter for filter in filters if filter['Scan Number'] == filterNum][0]
                addJanineData(filter)
            if len(notInDB) > 0:
                session['notInJSON'] = [addChoicesToDict(filter) for filter in notInDB]
                return redirect(url_for("corrections"))
            else:
                return redirect(url_for("janinescrape"))
    elif request.method == 'GET':
        return render_template("fileupload.html", form=form)


@app.route("/upload_zip", methods=["GET", "POST"])
@login_required
def upload_zip():
    form = UploadZipForm()
    user = User.query.filter_by(id=session.get('user_id')).first().email
    if request.method == 'POST':
        if form.validate == False:
            return render_template("zip_upload.html")
        patientNumber = form.patientNumber.data
        filterNumber = form.filterNumber.data
        app.logger.info("{} uploaded a zip file.".format(user))
        f = request.files.getlist('upfile')
        file = f[0]
        if os.path.splitext(secure_filename(file.filename))[1] == ".zip":
            newFile = uploadFile(file)
            zip_parser.extract_files(newFile, form.patientNumber.data, form.filterNumber.data)
            flash("Data for {}-{} has been added".format(patientNumber, filterNumber))
            return redirect(url_for("upload_zip"))
        else:
            # TODO insert flash error message.
            return redirect(url_for("upload_zip"))
    elif request.method == 'GET':
        return render_template("zip_upload.html", form=form)


@app.route("/corrections", methods=["GET", "POST"])
@login_required
def corrections():
    form = CorrectionsForm()
    if request.method == 'POST':
        if form.validate == False:
            return render_template("corrections.html", form=form)
        for iii, item in enumerate(form.orphans.entries):
            relevant_filter = session['notInJSON'][iii]
            old_filter_num = relevant_filter['Scan Number']
            relevant_filter['Scan Number'] = item.data
            relevant_filter.pop('choices')
            if relevant_filter['Scan Number'] != "":
                addJanineData(relevant_filter)
            else:
                flash("Filter with number {} was ignored.".format(old_filter_num))
        session.pop("notInJSON")
        return redirect(url_for('janinescrape'))
    elif request.method == 'GET':
        session.modified = True
        try:
            orphans = session['notInJSON']
        except:
            print("NotInJSON does not exist")
            return redirect(url_for("janinescrape"))
        for iii, orphan in enumerate(orphans):
            form.orphans.append_entry()
            setattr(form.orphans.entries[iii], 'id', "orphans-" + orphan['Scan Number'])
            form.orphans.entries[iii].label = orphan['Scan Number']
            form.orphans.entries[iii].choices = [(item, item) for item in orphan['choices']]
        return render_template("corrections.html", form=form)

@app.route("/", methods=["GET", "POST"])
@app.route("/all", methods=["GET", "POST"])
@login_required
def all():
    return render_template("all.html")

api.add_resource(filter, "/api")
api.add_resource(ApiLogin, "/api/login")
api.add_resource(TokenRefresh, "/api/tokenrefresh")
api.add_resource(All_Patients, "/api/all")
api.add_resource(Janine_DidNot, "/api/JanineDidNot")

def uploadFile(file):
    user = User.query.filter_by(id=session.get('user_id')).first().email
    upload_file = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    file.save(upload_file)
    upsize = int(round(int(os.stat(upload_file).st_size) / 1024))
    app.logger.info("{} uploaded a {}kb file".format(user, upsize))
    newFile = os.path.abspath(upload_file)
    return newFile