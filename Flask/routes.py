from bokeh.embed import components
from flask import Flask, render_template
from flask_restful import Api
from Flask.resources import filter
import os
from ChartMakers.bokeh_maker import create_hover_tool, create_histogram

app = Flask(__name__)
api = Api(app)

@app.route("/img/<string:patient_number>/<string:parameter_name>", methods=["GET"])
def chart(patient_number, parameter_name):

    hover = create_hover_tool()
    title_string = parameter_name + " vs. PSA for " + patient_number
    plot = create_histogram(patient_number, parameter_name, title_string, "Dates",
                            parameter_name, hover)
    script, div = components(plot)
    return render_template("chart.html", parameter_name=parameter_name, patient_number=patient_number,
                           the_div=div, the_script=script)

api.add_resource(filter, "/api/<string:patient_number>/<string:filter_number>")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run('localhost', port=port, debug=True)