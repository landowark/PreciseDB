# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addSample.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from AddSamples import sample_adder as samad

class Ui_Dialog(QDialog):

    def setupUi(self, Dialog):

        self.thisDialog = Dialog
        self.thisDialog.setObjectName("Dialog")
        self.thisDialog.resize(678, 560)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../UI/icons/logo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.thisDialog.setWindowIcon(icon)

        self.gridLayoutWidget = QtWidgets.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(13, 19, 651, 520))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.Sample_Number = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.Sample_Number.setObjectName("Sample Number")

        self.gridLayout.addWidget(self.Sample_Number, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)

        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.Accept)
        self.buttonBox.rejected.connect(self.Reject)
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)

        self.Patient_Number = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.Patient_Number.setText("")
        self.Patient_Number.setClearButtonEnabled(False)
        self.Patient_Number.setObjectName("Patient Number")

        self.gridLayout.addWidget(self.Patient_Number, 0, 0, 1, 1)

        self.calendarWidget = QtWidgets.QCalendarWidget(self.gridLayoutWidget)
        self.calendarWidget.setVerticalHeaderFormat(QtWidgets.QCalendarWidget.NoVerticalHeader)
        self.calendarWidget.setObjectName("calendarWidget")
        self.gridLayout.addWidget(self.calendarWidget, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.thisDialog.setWindowTitle(_translate("Dialog", "Add Sample"))
        self.Sample_Number.setPlaceholderText(_translate("Dialog", "Sample Number"))
        self.Patient_Number.setPlaceholderText(_translate("Dialog", "Patient Number"))

    def Accept(self):
        patNum = str(self.Patient_Number.text())
        samNum = str(self.Sample_Number.text())
        dateRec = str(self.calendarWidget.selectedDate().toPyDate())
        samad.add_from_UI(patNum, samNum, dateRec)
        self.thisDialog.close()

    def Reject(self):
        self.thisDialog.close()
        #pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

