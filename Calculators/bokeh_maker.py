import math

from bokeh.models import (HoverTool, FactorRange, Plot, LinearAxis, Grid,
                          Range1d)
from bokeh.plotting import figure


def create_hover_tool():
    # we'll code this function in a moment
    return None


def create_histogram(data, title, x_name, y_name, hover_tool=None,
                     width=1200, height=600):
    p = figure(plot_width=width, plot_height=height, title=title, x_axis_label=x_name, y_axis_label=y_name)
    psa_x = data['psaDates']
    psa_y = data['psaLevels']
    para_x = data['parameterDates']
    para_y = data['parameterLevels']

    p.y_range = Range1d(start=0, end=int(math.ceil(max(para_y) / 1000.0)) * 1000)
    p.extra_y_ranges = {"foo": Range1d(start=0, end=max(psa_y))}

    p.line(psa_x, psa_y, line_width=2, color='navy', alpha=0.6, y_range_name="foo")
    p.line(para_x, para_y, line_width=2, color = 'red')
    p.add_layout(LinearAxis(y_range_name="foo"), 'right')

    return p
