# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calendar.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Calendar(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Date Received")
        Dialog.resize(682, 574)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(150, 500, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.calendarWidget = QtWidgets.QCalendarWidget(Dialog)
        self.calendarWidget.setGeometry(QtCore.QRect(40, 90, 592, 374))
        self.calendarWidget.setObjectName("calendarWidget")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


def getDate(title='no prompt passed to widget'):
    import sys
    app = QtWidgets.QApplication.instance()  # checks if QApplication already exists
    if app == None:  # create QApplication if it doesnt exist
        app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Calendar()
    ui.setupUi(Dialog)
    if Dialog.exec_():
        selectedDate = ui.calendarWidget.selectedDate()
        ui.pydate = selectedDate.toPyDate()
        return (ui.pydate)

if __name__ == "__main__":
    print(getDate())