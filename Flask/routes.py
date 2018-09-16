from bokeh.embed import components
from flask import Flask, render_template, session, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_restful import Api
from Flask.resources import filter, logon, TokenRefresh
from Flask.forms import LoginForm
from Classes.models import User, db
import os
from ChartMakers.bokeh_maker import create_hover_tool, create_histogram
from flask_jwt_extended import JWTManager

app = Flask(__name__)
api = Api(app)
Bootstrap(app)
# Must be done before db.init
basedir = os.path.abspath(os.path.relpath("DB_DIR"))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "database.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "development-key"
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'

jwt = JWTManager(app)
db.init_app(app)


@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/precise/home")
def home():
    if 'email' in session:
        return render_template("home.html")
    else:
        return redirect(url_for('login'))

@app.route("/precise/login", methods=["GET", "POST"])
def login():
    if 'email' not in session:
        form = LoginForm()
        if request.method == "POST":
            if form.validate == False:
                return render_template("login.html", form=form)
            else:
                email = form.email.data
                password = form.password.data
                user = User.query.filter_by(email=email).first()
                if user is not None and user.check_password(password):
                    session['email'] = email
                    return redirect(url_for("home"))
                else:
                    return redirect(url_for("login"))
        elif request.method == "GET":
            return render_template("login.html", form=form)
    else:
        return redirect(url_for('home'))

@app.route("/precise/img/<string:patient_number>/<string:parameter_name>", methods=["GET"])
def chart(patient_number, parameter_name):
    if 'email' in session:
        hover = create_hover_tool()
        title_string = parameter_name + " vs. PSA for " + patient_number
        plot = create_histogram(patient_number, parameter_name, title_string, "Dates",
                                parameter_name, hover)
        script, div = components(plot)
        return render_template("chart.html", parameter_name=parameter_name, patient_number=patient_number,
                               the_div=div, the_script=script)
    else:
        return redirect(url_for('login'))

@app.route("/precise/logout")
def logout():
    if 'email' in session:
        session.pop('email', None)
        return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

api.add_resource(filter, "/precise/api")
api.add_resource(logon, "/precise/api/login")
api.add_resource(TokenRefresh, "/precise/api/tokenrefresh")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run('localhost', port=port, debug=True)
