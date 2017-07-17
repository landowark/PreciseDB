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
import sys
import datetime

def main():
    from PyQt5 import QtGui, QtWidgets  # for calling QApplication in main (necessary to prevent multiple calls in fxns)
    import lw_calendar as cal  # custom calendar widget to choose dates
    import lw_textinput as txti  # custom text input widget
    app = QtWidgets.QApplication.instance()
    # checks if QApplication already exists
    if not app: # create QApplication if it doesnt exist
        app = QtWidgets.QApplication(sys.argv)
    patientNumber = namer.parsePatient(txti.getText('Insert patient number.')) #gui ask for patient and parse
    filterNumber = namer.parseFilter(txti.getText('Insert filter number')) #gui ask for filter and parse
    #check if patient already exists
    patient_exists = mng.findPatient(patientNumber)
    if patient_exists == False:
        print('Previously unseen patient. Adding to database.')
        newPat = ptz.Patient(patNum=patientNumber)
        mng.addPatient(newPat)
    else:
        print('Previously seen patient.')
    #check if filter already exists for this patient
    if mng.filterExists(patientNumber, filterNumber) == False:
        print('Previously unseen filter. Adding to database.')
        #create new filter with default values
        newFilt = fltz.Filter(filtNum=filterNumber)
        newFilt.DateRec = str(cal.getDate('Select date sample was received'))
        # retrieve existing patient and update filters
        dicto = mng.retrieveDoc(patientNumber)
        dicto['filters'].append(newFilt)
        #save
        mng.shoveDoc(dicto)
    else:
        print('Previously seen filter.')

def add_scrape(input_patient, input_filter, input_received):
    # Add a patient scraped from the access database.
    patientNumber = namer.parsePatient(input_patient)
    filterNumber = namer.parseFilter(input_filter)
    # check if patient already exists
    patient_exists = mng.findPatient(patientNumber)
    if patient_exists == False:
        print('Previously unseen patient. Adding to database.')
        newPat = ptz.Patient(patNum=patientNumber)
        mng.addPatient(newPat)
    else:
        print('Previously seen patient.')
    # check if filter already exists for this patient
    if mng.filterExists(patientNumber, filterNumber) == False:
        print('Previously unseen filter. Adding to database.')
        dateReceived = datetime.datetime.strptime(input_received, '%Y-%m-%d').date()
        #scrape time point
        if patient_exists == False:
            print("First time point for this patient. Using +00m")
            delta = 0
        else:
            firstDate = mng.getFirstSampleDate(patientNumber)
            delta = round(int((dateReceived - firstDate).days)/30)
        timePoint = "+%sm" % str(delta).zfill(2)
        newFilt = fltz.Filter(filtNum=filterNumber, tPoint=timePoint)
        newFilt.DateRec = input_received
        dicto = mng.retrieveDoc(patientNumber)
        dicto['filters'].append(newFilt)
        mng.shoveDoc(dicto)
    else:
        print('Previously seen filter.')

if __name__ == '__main__':
    main()
    sys.exit()