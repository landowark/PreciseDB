# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1064, 606)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 10, 291, 511))
        self.treeWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.treeWidget.setAutoExpandDelay(10)
        self.treeWidget.setObjectName("treeWidget")
        self.teloButton = QtWidgets.QPushButton(self.centralwidget)
        self.teloButton.setGeometry(QtCore.QRect(330, 480, 150, 46))
        self.teloButton.setObjectName("teloButton")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(320, 10, 721, 451))
        self.widget.setObjectName("widget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1064, 38))
        self.menubar.setObjectName("menubar")
        self.menuSamples = QtWidgets.QMenu(self.menubar)
        self.menuSamples.setObjectName("menuSamples")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionAdd_Sample = QtWidgets.QAction(MainWindow)
        self.actionAdd_Sample.setObjectName("actionAdd_Sample")
        self.menuSamples.addAction(self.actionAdd_Sample)
        self.menubar.addAction(self.menuSamples.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "Patients"))
        self.teloButton.setToolTip(_translate("MainWindow", "Generate Telomgraphs for selected filters."))
        self.teloButton.setText(_translate("MainWindow", "Generate"))
        self.menuSamples.setTitle(_translate("MainWindow", "Samples"))
        self.actionAdd_Sample.setText(_translate("MainWindow", "Add Sample"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

