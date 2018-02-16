# -*- coding: utf-8 -*-
"""
Spyder Editor

This module will serve as the way to create a new patient num in mongo if one doesn't 
exist and then add a filter to the specified patient

@author: Landon
"""

from MongoInterface import mongo as mng
from Classes import filterizer as fltz, patientizer as ptz, namer
import sys
import datetime
import logging
from PyQt5.QtWidgets import QFileDialog, QApplication

logger = logging.getLogger("mainUI.sample_adder")

def add(patientNumber, filterNumber, dateRec):
    patientNumber = namer.parsePatient(patientNumber)
    filterNumber = namer.parseFilter(filterNumber)
    #check if patient already exists
    patient_exists = mng.patientExists(patientNumber)
    if patient_exists == False:
        logging.info('Previously unseen patient: %s. Adding to database.' % patientNumber)
        newPat = ptz.Patient(patNum=patientNumber)
        mng.addPatient(newPat)
    else:
        logging.info('Previously seen patient: %s' % patientNumber)
    # check if filter already exists for this patient
    if mng.filterExists(patientNumber, filterNumber) == False:
        logging.info('Previously unseen filter: %s. Adding to database.' % filterNumber)
        # dateReceived = datetime.datetime.strptime(dateRec, '%Y-%m-%d').date()
        # scrape time point
        # set initial time since last sample = 0
        delta = 0
        # if the patient didn't exist back when patient_exists was set will use deltatime 0
        if patient_exists == False:
            logging.info("First time point for this patient. Using +00m")
        # else it will calculate delta time until it finds a timepoint not currently in use
        else:
            delta = deltaTimer(patientNumber=patientNumber, dateRec=dateRec)
            logging.info("Constructing timepoint for %s using Date Received" % filterNumber)
        # set timepoint string
        timePoint = "+%sm" % str(delta).zfill(2)
        newFilt = fltz.Filter(tPoint=timePoint)
        newFilt.DateRec = dateRec
        dicto = mng.retrieveDoc(patientNumber)
        dicto['filters'][filterNumber] = newFilt
        mng.shoveDoc(dicto)
    else:
        logging.info('Previously seen filter: %s.' % filterNumber)


def deltaTimer(patientNumber="MB0000PR", dateRec=datetime.date.today()):
    options = [0, 2, 6, 12, 18, 24, 30]
    firstDate = mng.getFirstSampleDate(patientNumber)
    delta = round(int((dateRec - firstDate).days) / 30)
    delta = min(options, key=lambda x: abs(x - delta))
    logging.debug("Hit delta: %s" % delta)
    return delta

def table_scraper():
    import pandas as pd
    import numpy as np
    app = QApplication(sys.argv)
    # Select database source .xlsx
    database_file = QFileDialog.getOpenFileName(None, 'Select source sheet', "C:\\Users\\Landon\\Dropbox\\Documents\\Student\ Work", filter="xlsx(*.xlsx)")
    samples = pd.read_excel(database_file)
    # Get list of patients
    patients = np.unique(samples['PatientID'])
    # Iterate through patients
    for patient in patients:
        # get cells where PatientID == patient number, sort by date
        frame = samples.loc[samples['PatientID'] == patient].sort_values("DateReceived")
        for index, row in frame.iterrows():
            #print(datetime.datetime.strftime(row['DateReceived'].to_pydatetime(), "%Y-%m-%d"))
            add(['PatientID'], row['FilterID'], datetime.datetime.strftime(row['DateReceived'].to_pydatetime(), "%Y-%m-%d"))
    sys.exit(app.exec_())

if __name__ == '__main__':
    add(patientNumber="MB0000PR", filterNumber="14AA0001", dateRec=datetime.date.today())
    sys.exit()