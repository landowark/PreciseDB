# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QGraphicsView, QMenuBar, QPushButton, QStatusBar, QGridLayout
import pymongo as mng
from MongoInterface import mongo
from ScrapeTeloView import telomgraph_emulator as te
import os

class Ui_MainWindow(object):


    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1064, 606)
        # set layout to grid
        grid = QGridLayout()
        # config central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setLayout(grid)

        # View of Patient list
        self.treeWidget = QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 10, 291, 511))
        self.treeWidget.setObjectName("treeWidget")
        # View of Matplotlib... maybe
        self.graphicsView = QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(330, 10, 711, 281))
        self.graphicsView.setObjectName("graphicsView")
        # Generate button
        self.teloButton = QPushButton(self.centralwidget)
        self.teloButton.setGeometry(QtCore.QRect(330, 480, 150, 46))
        self.teloButton.setObjectName("teloButton")


        # Main Window config stuff
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1064, 38))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        grid.addWidget(self.treeWidget, 0, 1)
        grid.addWidget(self.graphicsView, 0, 2)
        grid.addWidget(self.teloButton, 1, 2)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Generate patient list
        self.createDataTree()

        # Connect buttons
        self.teloButton.clicked.connect(self.teloButtonClicked)


    def retranslateUi(self, MainWindow):

        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Patients"))
        self.teloButton.setToolTip(_translate("MainWindow", "Generate Telomgraphs for selected filters."))
        self.teloButton.setText(_translate("MainWindow", "Generate"))

    def createDataTree(self):
        db = mng.MongoClient().prostate_actual.patient
        for patient in db.find():
            parent = QTreeWidgetItem(self.treeWidget)
            parent.setText(0, patient['_id'])
            parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for filter in sorted(patient['filters'].keys()):
                filt_TP = filter + " " + patient['filters'][filter]['tPoint']
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                child.setText(0, filt_TP)
                child.setCheckState(0, Qt.Unchecked)

    def teloButtonClicked(self):
        self.statusbar.showMessage("Telo Button Clicked!")
        root = self.treeWidget.invisibleRootItem()
        patient_count = root.childCount()
        samples_list = []
        checked = {}
        for iii in range(patient_count):
            patient = root.child(iii)
            #checked_sweeps = []
            filter_count = patient.childCount()
            for jjj in range(filter_count):
                filter = patient.child(jjj)
                if filter.checkState(0) == Qt.Checked:
                    #checked_sweeps.append(filter.text(0).split(" ")[0])
                    samples_list.append((patient.text(0), filter.text(0).split(" ")[0]))
            #checked[patient.text(0)] = checked_sweeps
        for sample in samples_list:
            dicto = mongo.get_filter_by_number(sample[0], sample[1])
            timePoint = dicto['tPoint']
            sample_title = sample[0] + " " + timePoint + " " + sample[1] + ".xlsx"
            te.telomgraph(dicto, os.path.join("C:\\Users\\Landon\\Desktop", sample_title))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

