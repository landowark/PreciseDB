# -*- coding: utf-8 -*-
"""
Spyder Editor

This module will serve as the way to create a new patient num in mongo if one doesn't
exist and then add a filter to the specified patient

@author: Landon
"""

from DB_DIR import mongo as mng
from Classes import filterizer as fltz, patientizer as ptz, namer
import datetime
import logging

logger = logging.getLogger("Flask.addSample")

def add(patientNumber, filterNumber, dateRec, mLBlood, initials, institute, receiver):
    patientNumber = namer.parsePatient(patientNumber) #gui ask for patient and parse
    filterNumber = namer.parseFilter(filterNumber) #gui ask for filter and parse
    #check if patient already exists
    patient_exists = mng.patientExists(patientNumber)
    if patient_exists == False:
        logger.info('Previously unseen patient {}. Adding to database.'.format(patientNumber))
        newPat = ptz.Patient(patNum=patientNumber)
        newPat.initials = initials
        newPat.institute = institute
        newPat.DateRec = dateRec
        newPat.mLBlood = mLBlood
        newPat.receiver = receiver
        newPat.patient_num = len(mng.getPatientList()) + 1
        mng.addPatient(newPat)
    else:
        logger.info('Previously seen patient: {}.'.format(patientNumber))

    try:
        patient_increment = newPat.patient_num
    except:
        patient_increment = 0
    #check if filter already exists for this patient
    if mng.filterExists(patientNumber, filterNumber) == False:
        logger.info('Previously unseen filter: {}. Adding to database.'.format(filterNumber))
        dateReceived = datetime.datetime.strptime(dateRec, '%Y-%m-%d').date()
        # scrape time point
        if patient_exists == False:
            logger.info("First time point for patient {}. Using +00m".format(patientNumber))
            delta = 0
        else:
            firstDate = mng.getFirstSampleDate(patientNumber)
            delta = deltaTimer(dateReceived, firstDate)
        timePoint = "+%sm" % str(delta).zfill(2)
        #create new filter with default values
        newFilt = fltz.Filter(filtNum=filterNumber, tPoint=timePoint)

        # retrieve existing patient and update filters
        dicto = mng.retrieveDoc(patientNumber)
        dicto['filters'][filterNumber] = newFilt.jsonable()
        #save
        mng.shoveDoc(dicto)
        #return dicto
    else:
        logger.info('Previously seen filter" {}. Exiting'.format(filterNumber))
    # Return value to determine messaging
    return patient_increment

def deltaTimer(dateRec=datetime.date.today(), firstDate=datetime.date.today()):
    options = [0, 2, 6, 12, 18, 24, 30]
    months = round(int((dateRec - firstDate).days) / 30)
    delta = min(options, key=lambda x:abs(x-months))
    return delta
