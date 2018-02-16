# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QGraphicsView, QMenuBar, QPushButton, QStatusBar, QGridLayout, QMainWindow
import pymongo as mng
from MongoInterface import mongo
from ScrapeTeloView import telomgraph_emulator as te

import os
from PyQt5.QtGui import QIcon
from UI import addSample
import logging
from logging.handlers import RotatingFileHandler
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import numpy as np
from UI.Figure import MyMplCanvas




#set up logging.
logger = logging.getLogger("mainUI")
logger.setLevel(logging.DEBUG)
#fh = RotatingFileHandler('/home/landon/Logs/torrentbot.log', maxBytes=50000, backupCount=3)
fh = RotatingFileHandler('C:\\Users\\Landon\\Desktop\\QP.log', maxBytes=50000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

class Ui_MainWindow(object):


    def setupUi(self, MainWindow):

        self.logger = logging.getLogger("mainUI.UI")
        self.logger.debug("Starting up UI.")


        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1064, 606)
        # set layout to grid
        grid = QGridLayout()

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../UI/icons/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)

        # config central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setLayout(grid)




        # View of Patient list
        self.treeWidget = QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 10, 291, 511))
        self.treeWidget.setObjectName("treeWidget")
        # TODO View of Matplotlib... when I get it working
        self.matplot = MyMplCanvas(self.centralwidget, width=5, height=4, dpi=100)
        # self.graphicsView = QGraphicsView(self.centralwidget)
        # self.graphicsView.setGeometry(QtCore.QRect(330, 10, 711, 281))
        # self.graphicsView.setObjectName("graphicsView")

        # self.matplot = QtWidgets.QWidget(self.centralwidget)
        # self.matplot.setGeometry(QtCore.QRect(320, 10, 721, 451))
        # self.matplot.setObjectName("matplot")



        # Generate button
        self.teloButton = QPushButton(self.centralwidget)
        self.teloButton.setGeometry(QtCore.QRect(330, 480, 150, 46))
        self.teloButton.setObjectName("teloButton")


        # Main Window config stuff
        MainWindow.setCentralWidget(self.centralwidget)
        # config menubar.
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1064, 38))
        self.menubar.setObjectName("menubar")
        self.menuSamples = QtWidgets.QMenu(self.menubar)
        self.menuSamples.setObjectName("menuSamples")
        self.actionAdd_Sample = QtWidgets.QAction(MainWindow)
        self.actionAdd_Sample.setObjectName("actionAdd_Sample")
        self.menuSamples.addAction(self.actionAdd_Sample)
        self.menubar.addAction(self.menuSamples.menuAction())

        MainWindow.setMenuBar(self.menubar)

        # Config statusbar
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        # Add widgets to grid
        grid.addWidget(self.treeWidget, 0, 1)
        grid.addWidget(self.matplot, 0, 2)
        grid.addWidget(self.teloButton, 1, 2)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Generate patient list
        self.updateDataTree()
        # Sort items.. works pretty good
        self.treeWidget.sortItems(0, 0)

        # Connect buttons
        self.teloButton.clicked.connect(self.teloButtonClicked)
        self.actionAdd_Sample.triggered.connect(self.addSampleDialog)
        self.treeWidget.currentItemChanged.connect(self.activePatientChart)


    def retranslateUi(self, MainWindow):

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Patients"))
        self.teloButton.setToolTip(_translate("MainWindow", "Generate Telomgraphs for selected filters."))
        self.teloButton.setText(_translate("MainWindow", "Generate"))
        self.menuSamples.setTitle(_translate("MainWindow", "Samples"))
        self.actionAdd_Sample.setText(_translate("MainWindow", "Add Sample"))

    def updateDataTree(self):
        db = mng.MongoClient().prostate_actual.patient
        self.logger.info("Checking MongoDB for patients.")
        for patient in db.find():
            parent = QTreeWidgetItem(self.treeWidget)
            self.logger.debug("Adding %s to patients." % patient['_id'])
            patient_id = patient['_id']
            parent.setText(0, patient_id)
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for filter in sorted(patient['filters'].keys()):
                filt_TP = patient['filters'][filter]['tPoint'] + " " + filter
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                self.logger.debug("Adding %s to %s." % (filt_TP, patient_id))
                child.setText(0, filt_TP)
                child.setCheckState(0, Qt.Unchecked)

    def teloButtonClicked(self):
        root = self.treeWidget.invisibleRootItem()
        self.logger.info("Started export of telomgraphs.")
        # Count number of patients
        patient_count = root.childCount()
        samples_list = []
        # iterate through patients
        for iii in range(patient_count):
            patient = root.child(iii)
            # count number of filters per patient
            filter_count = patient.childCount()
            # iterate through filters
            for jjj in range(filter_count):
                filter = patient.child(jjj)
                # check filter item status checked/unchecked
                if filter.checkState(0) == Qt.Checked:
                    # add checked item to sample list for telomgraph
                    samples_list.append((patient.text(0), filter.text(0).split(" ")[1]))
        for sample in samples_list:
            patient_number = sample[0]
            filter_number = sample[1]
            timePoint = mongo.get_filter_by_number(patient_number, filter_number)['tPoint']
            sample_title = sample[0] + " " + timePoint + " " + sample[1] + ".xlsx"
            #self.statusbar.showMessage("Exporting %s" % sample_title)
            te.telomgraph(patient_number, filter_number, os.path.join("C:\\Users\\Landon\\Desktop", sample_title))
        self.statusbar.showMessage("Export done!")

    def addSampleDialog(self):
        self.sampleDialog = QtWidgets.QDialog()
        self.ui = addSample.Ui_Dialog()
        self.ui.setupUi(self.sampleDialog)
        self.sampleDialog.exec_()
        self.updateDataTree()
        #self.ui.exec_()

    def activePatientChart(self):
        patient_number = self.treeWidget.currentItem().text(0)
        if patient_number == "MB0000PR":
            pass
        else:
            self.matplot.update_figure(patient_number)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # app.setWindowIcon(QIcon(icon_location))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

