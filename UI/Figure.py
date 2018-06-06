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
        self.axes.set_ylabel("PSA level")

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def update_figure(self, patient_number):
        try:
            # get axis values
            psaDates, psaLevels, parameterDates, parameterLevels, fullDates = cm.calculate_axes(patient_number, "meanInt")
            text_box = cm.createTextBox(patient_number)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            treatments = cm.getTreatments(patient_number)
            # reporter of treatment names.
            #print([xxx['name'] for xxx in treatments])
            self.axes.cla()
            self.axes.set_xticks(fullDates)
            self.axes.set_xticklabels([mdates.num2date(x).strftime('%Y-%m-%d') for x in fullDates], rotation=90)
            self.axes.set_ylabel("PSA level")
            for trx in treatments:
                try:
                    if "Bical" in trx['name']:
                        facecolor = 'blue'
                    elif "RT" in trx['name']:
                        facecolor = 'orange'
                    elif "Leu" in trx['name']:
                        facecolor = 'red'
                    else:
                        facecolor = 'gray'
                    bbox_props = dict(boxstyle="square,pad=0.3", fc=facecolor, ec="b", lw=2, alpha=0.7)
                    self.axes.axvspan(trx['start'], trx['end'], facecolor=facecolor, alpha=0.25)
                    self.axes.text(((trx['start'] + trx['end']) / 2), 1, trx['name'], color='white', va="bottom", ha='center',
                             size=15, rotation=90, bbox=bbox_props)
                except ValueError as e:
                    print(e)
                    continue


            self.axes.text(0.75, 0.55, text_box, transform=self.axes.transAxes, fontsize=14,
                     verticalalignment='top', bbox=props)
            self.axes.plot(psaDates, psaLevels, 'r')
            self.draw()
        except Exception as e:
            print(e)
