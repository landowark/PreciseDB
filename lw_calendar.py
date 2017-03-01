# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/landon/Documents/Python/UI/calendar.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
#import sys
#import datetime

class Calendar(object):
    def setupUi(self, Dialog, title):
        Dialog.setObjectName("Dialog")
        Dialog.resize(682, 574)
        Dialog.setWindowTitle(title)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(150, 500, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.calendarWidget = QtGui.QCalendarWidget(Dialog)
        self.calendarWidget.setGeometry(QtCore.QRect(40, 90, 592, 374))
        self.calendarWidget.setObjectName("calendarWidget")
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        if Dialog.exec_():
            selectedDate = self.calendarWidget.selectedDate()
            self.pydate = selectedDate.toPyDate()
        else:
            print('False')
   
def getDate(title='no prompt passed to widget'):
#    app = QtGui.QApplication.instance() # checks if QApplication already exists 
#    if app == None: # create QApplication if it doesnt exist 
#        app = QtGui.QApplication(sys.argv) 
    ui = Calendar()
    ui.setupUi(QtGui.QDialog(), title)
    return(ui.pydate)
    
if __name__ == '__main__':
    print(getDate())