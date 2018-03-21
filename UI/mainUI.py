# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QGraphicsView, QMenuBar, QPushButton, QStatusBar, QGridLayout, QTreeWidgetItemIterator
import pymongo as mng
from MongoInterface import mongo
from ScrapeTeloView import telomgraph_emulator as te
import os
from UI import addSample
import logging
from logging.handlers import RotatingFileHandler
from UI.Figure import MyMplCanvas


#set up logging.
logger = logging.getLogger("mainUI")
logger.setLevel(logging.DEBUG)
fh = RotatingFileHandler('C:\\Users\\Landon\\Desktop\\Debugging\\QP.log', maxBytes=50000, backupCount=3)
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
        self.treeWidget.setMaximumWidth(400)
        self.treeWidget.setObjectName("treeWidget")

        # matplotlib widget
        self.matplot = MyMplCanvas(self.centralwidget, width=5, height=4, dpi=100)

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
        self.createDataTree()
        # Sort items... works pretty good
        self.treeWidget.sortItems(0, 0)

        # Connect buttons
        self.teloButton.clicked.connect(self.teloButtonClicked)
        self.actionAdd_Sample.triggered.connect(self.addSampleDialog)
        self.treeWidget.currentItemChanged.connect(self.activePatientChart)
        # Quick iterator check
        # iterator = QTreeWidgetItemIterator(self.treeWidget, QTreeWidgetItemIterator.HasChildren)
        # while iterator.value():
        #     item = iterator.value().text(0)
        #     print(iterator.value())
        #     iterator += 1


    def retranslateUi(self, MainWindow):

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Patients"))
        self.teloButton.setToolTip(_translate("MainWindow", "Generate Telomgraphs for selected filters."))
        self.teloButton.setText(_translate("MainWindow", "Generate"))
        self.menuSamples.setTitle(_translate("MainWindow", "Samples"))
        self.actionAdd_Sample.setText(_translate("MainWindow", "Add Sample"))

    # TODO split into create and update data tree
    def createDataTree(self):
        db = mng.MongoClient().prostate_actual.patient
        self.logger.info("Checking MongoDB for patients.")
        TreeWidgetItems = QTreeWidgetItem(self.treeWidget)
        print(TreeWidgetItems)
        for patient in db.find():
            self.shove_doc_to_tree(patient)


    def updatePatient(self, patientNum, filterNum):
        db = mng.MongoClient().prostate_actual.patient
        # Use iterator to go through all items in tree
        if mongo.patientExists(patientNum):
            try:
                iterator = QTreeWidgetItemIterator(self.treeWidget, QTreeWidgetItemIterator.HasChildren)
                while iterator.value():
                    item = iterator.value().text(0)
                    if item == patientNum:
                        print("Attempting to update %s with %s." % (patientNum, filterNum))
                        parent = iterator.value()
                        patient = mongo.retrieveDoc(patientNum)
                        self.shove_filter_to_tree(filterNum, parent, patient, patientNum)
                    iterator += 1
            except Exception as e:
                self.logger.debug(e)
        else:
            self.shove_doc_to_tree(patientNum)
        self.treeWidget.sortItems(0, 0)


    def shove_doc_to_tree(self, patient):
        self.logger.debug("Adding %s to patients." % patient['_id'])
        parent = QTreeWidgetItem(self.treeWidget)
        patient_id = patient['_id']
        parent.setText(0, patient_id)
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for filter in sorted(patient['filters'].keys()):
            self.shove_filter_to_tree(filter, parent, patient, patient_id)

    def shove_filter_to_tree(self, filter, parent, patient, patient_id):
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
        try:
            self.sampleDialog = QtWidgets.QDialog()
            self.ui = addSample.Ui_Dialog()
            self.ui.setupUi(self.sampleDialog)
            self.sampleDialog.exec_()
            # TODO make new function updateDataTree
            print("Reached end of addSampleDialog")
            self.updatePatient(self.ui.Patient_Number.text(), self.ui.Sample_Number.text())
        except Exception as e:
            self.logger.debug(e)


    def activePatientChart(self):
        # Updates matplotlib widget based on current patient selection.
        patient_number = self.treeWidget.currentItem().text(0)
        # Skip test patient.
        if patient_number == "MB0000PR":
            pass
        else:
            # Run update figure function of matplotlib widget in Figure.py
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

