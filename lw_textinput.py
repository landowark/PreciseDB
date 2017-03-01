# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/landon/Documents/Python/UI/text.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
#import sys

class textBox(object):
    def setupUi(self, Dialog, title):
        Dialog.setObjectName("Dialog")
        Dialog.resize(560, 85)
        Dialog.setWindowTitle(title)
        self.plainTextEdit = QtGui.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 10, 541, 31))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(360, 50, 176, 27))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        if Dialog.exec_():
            self.userInput = self.plainTextEdit.toPlainText()
        else:
            self.userInput = ''
            
def getText(title='no prompt passed to widget'):
#    app = QtGui.QApplication.instance() # checks if QApplication already exists 
#    if not app: # create QApplication if it doesnt exist 
#        app = QtGui.QApplication(sys.argv)
    ui = textBox()
    ui.setupUi(QtGui.QDialog(), title)
    return(ui.userInput)
    
if __name__ == '__main__':
    print(getText())