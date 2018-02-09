# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/landon/Documents/Python/UI/text.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class textBox(object):
    def setupUi(self, Dialog, title="Dialog"):
        Dialog.setObjectName("Dialog")
        Dialog.resize(560, 85)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 10, 541, 31))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(360, 50, 176, 27))
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(Dialog, title)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog, title):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate(title, title))

def getText(title):
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = textBox()
    ui.setupUi(Dialog, title)
    if Dialog.exec_():
        ui.userInput = ui.plainTextEdit.toPlainText()
    else:
        ui.userInput = ''
    return(ui.userInput)

if __name__ == "__main__":
    print(getText())