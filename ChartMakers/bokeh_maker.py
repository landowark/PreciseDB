'''

Making charts for 

'''


import math
from bokeh.models import (LinearAxis, Range1d, DatetimeTickFormatter, HoverTool)
from bokeh.plotting import figure
from bokeh.models.glyphs import Line
from bokeh.models.sources import ColumnDataSource
from DB_DIR import mongo as mng
from ChartMakers.chart_maker import calculate_axes
from matplotlib.dates import num2date
from datetime import datetime


def create_hover_tool():
    # we'll code this function in a moment
    return None

def create_histogram(patient_number, parameter_name, title, x_name, y_name, hover_tool=None,
                     width=1200, height=600):

    # grab relevant data from
    psaDates, psaLevels, parameterDates, parameterLevels, fullDates = calculate_axes(patient_number, parameter_name)
    data = {
        "patient_number": patient_number,
        "parameter_name": parameter_name,
        "psaDates": [num2date(date) for date in psaDates],
        "psaLevels": psaLevels,
        "parameterDates": [num2date(date) for date in parameterDates],
        "parameterLevels": parameterLevels,
        "fulldates": [datetime.strftime(num2date(date), "%Y-%m-%d") for date in fullDates]
    }

    psa_data = {'x':data['psaDates'], 'y':data['psaLevels'], 'labels':["PSA"] * len(data['psaDates'])}
    psa_source = ColumnDataSource(psa_data)
    psa_glyph = Line(x="x", y="y", line_color="red", line_width=6, line_alpha=0.6)

    parameter_data = {'x':data['parameterDates'], 'y':data['parameterLevels'], 'labels':[data['parameter_name']] * len(data['parameterDates'])}
    para_source = ColumnDataSource(parameter_data)
    para_glyph = Line(x="x", y='y', line_color="blue", line_width=6, line_alpha=0.6)

    p = figure(plot_width=width, plot_height=height, title=title, x_axis_label=x_name, y_axis_label=y_name, x_axis_type="datetime")

    # set chart y_range to end at the maximum values seen in all patients for parameter.
    max_y  = int(math.ceil(mng.get_parameter_maximum(data['parameter_name'])) / 1000.0) * 1000
    p.y_range = Range1d(start=0, end=max_y)
    # set extra range for psa levels
    p.extra_y_ranges = {"foo": Range1d(start=0, end=mng.get_parameter_maximum("PSA"))}
    p.xaxis.formatter = DatetimeTickFormatter(
        days=["%Y-%m-%d"],
        months=["%Y-%m-%d"],
        years=["%Y-%m-%d"],
    )
    p.add_glyph(psa_source, psa_glyph, y_range_name='foo')
    p.add_glyph(para_source, para_glyph)
    p.add_layout(LinearAxis(y_range_name="foo"), 'right')
    p.yaxis[1].axis_label = "PSA Level"

    h1 = HoverTool(tooltips=[('Parameter', '@labels'), ('Level', '@y')], line_policy='nearest')
    p.add_tools(h1)
    return p
