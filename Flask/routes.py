from bokeh.embed import components
from flask import Flask, make_response, request, render_template
from flask_restful import Api
from resources import filter
import os
from ScrapeTeloView.chart_maker import calculate_axes
from Calculators.bokeh_maker import create_hover_tool, create_histogram


app = Flask(__name__)
api = Api(app)


@app.route("/img/<string:patient_number>/<string:parameter_name>", methods=["GET"])
def chart(patient_number, parameter_name):
    psaDates, psaLevels, parameterDates, parameterLevels, fullDates = calculate_axes(patient_number, parameter_name)
    data = {
        "patient_number": patient_number,
        "parameter_name": parameter_name,
        "psaDates": psaDates,
        "psaLevels": psaLevels,
        "parameterDates": parameterDates,
        "parameterLevels": parameterLevels,
        "fulldates": fullDates
    }
    hover = create_hover_tool()
    title_string = parameter_name + " vs. PSA for " + patient_number
    plot = create_histogram(data, title_string, "days",
                            "bugs", hover)

    script, div = components(plot)
    #print(script)
    return render_template("chart.html", parameter_name=parameter_name, patient_number=patient_number,
                           the_div=div, the_script=script)


api.add_resource(filter, "/api/<string:patient_number>/<string:filter_number>")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run('localhost', port=port, debug=True)