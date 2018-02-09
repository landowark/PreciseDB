# -*- coding: utf-8 -*-
"""
Spyder Editor

This module will serve as the way to create a new patient num in mongo if one doesn't 
exist and then add a filter to the specified patient

@author: Landon
"""

from MongoInterface import mongo as mng
from Classes import filterizer as fltz, patientizer as ptz
import namer #custom regex functions
import sys
import datetime

def main():
    from PyQt5 import QtWidgets  # for calling QApplication in main (necessary to prevent multiple calls in fxns)
    from UI import lw_calendar as cal
    from UI import lw_textinput as txti
    app = QtWidgets.QApplication.instance()
    # checks if QApplication already exists
    if not app: # create QApplication if it doesnt exist
        app = QtWidgets.QApplication(sys.argv)
    patientNumber = namer.parsePatient(txti.getText('Insert patient number.')) #gui ask for patient and parse
    filterNumber = namer.parseFilter(txti.getText('Insert filter number')) #gui ask for filter and parse
    #check if patient already exists
    patient_exists = mng.patientExists(patientNumber)
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
    patient_exists = mng.patientExists(patientNumber)
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
        newFilt = fltz.Filter(tPoint=timePoint)
        newFilt.DateRec = input_received
        dicto = mng.retrieveDoc(patientNumber)
        dicto['filters'][filterNumber] = newFilt
        mng.shoveDoc(dicto)
    else:
        print('Previously seen filter.')

if __name__ == '__main__':
    main()
    sys.exit()