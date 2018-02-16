# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
from ScrapeTeloView import chart_maker as cm
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure(self, patient_number):
        try:
            # Build a list of 4 random integers between 0 and 10 (both inclusive)
            # l = [random.randint(0, 10) for i in range(4)]
            psaDates, psaLevels, parameterDates, parameterLevels, fullDates = cm.calculate_axes(patient_number, "meanInt")
            self.axes.cla()
            self.axes.set_xticks(fullDates)
            self.axes.set_xticklabels([mdates.num2date(x).strftime('%Y-%m-%d') for x in fullDates], rotation=90)

            self.axes.plot(psaDates, psaLevels, 'r')
            self.draw()
        except Exception as e:
            print(e)
