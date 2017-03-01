# -*- coding: utf-8 -*-
"""
Spyder Editor

This module will serve as the way to create a new patient num in mongo if one doesn't 
exist and then add a filter to the specified patient

@author: Landon
"""

import mongo as mng  #custom mongo database read/write funtions
import patientizer as ptz #custom patient class
import filterizer as fltz #custom filter class
import namer #custom regex functions
import lw_calendar as cal #custom calendar widget to choose dates
import lw_textinput as txti #custom text input widget
import sys
from PyQt5 import QtGui, QtWidgets #for calling QApplication in main (necessary to prevent multiple calls in fxns)

def main():
    app = QtWidgets.QApplication.instance()
    # checks if QApplication already exists
    if not app: # create QApplication if it doesnt exist 
        app = QtWidgets.QApplication(sys.argv)
    patientNumber = namer.parsePatient(txti.getText('Insert patient number.')) #gui ask for patient and parse
    filterNumber = namer.parseFilter(txti.getText('Insert filter number')) #gui ask for filter and parse
    #check if patient already exists
    if mng.findPatient(patientNumber) == False:
        print('Previously unseen patient. Adding to database.')
        newPat = ptz.Patient(patNum=patientNumber)
        mng.addPatient(newPat)            
    else:
        print('Previously seen patient.')
    #check if filter already exists for this patient
    if mng.findFilter(patientNumber, filterNumber) == False:
        print('Previously unseen filter. Adding to database.')
        newFilt = fltz.Filter(filtNum=filterNumber)
        newFilt.DateRec = str(cal.getDate('Select date sample was received'))
        dicto = mng.retrieveDoc(patientNumber)
        dicto['Filter_' + filterNumber] = newFilt
        mng.shoveDoc(dicto)
    else:
        print('Previously seen filter.')

if __name__ == '__main__':
    main()
    sys.exit()