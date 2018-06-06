# -*- coding: utf-8 -*-
"""
Spyder Editor

This module will serve as the way to create a new patient num in mongo if one doesn't
exist and then add a filter to the specified patient

@author: Landon
"""

from MongoInterface import mongo as mng
from Classes import filterizer as fltz, patientizer as ptz, namer
import datetime

def add(patientNumber, filterNumber, dateRec):
    patientNumber = namer.parsePatient(patientNumber) #gui ask for patient and parse
    filterNumber = namer.parseFilter(filterNumber) #gui ask for filter and parse
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
        dateReceived = datetime.datetime.strptime(dateRec, '%Y-%m-%d').date()
        # scrape time point
        if patient_exists == False:
            print("First time point for this patient. Using +00m")
            delta = 0
        else:
            firstDate = mng.getFirstSampleDate(patientNumber)
            delta = deltaTimer(dateReceived, firstDate)
        timePoint = "+%sm" % str(delta).zfill(2)
        print(timePoint)
        #create new filter with default values
        newFilt = fltz.Filter(filtNum=filterNumber, tPoint=timePoint)
        newFilt.DateRec = dateRec
        # retrieve existing patient and update filters
        dicto = mng.retrieveDoc(patientNumber)
        dicto['filters'][filterNumber] = newFilt
        #save
        mng.shoveDoc(dicto)
    else:
        print('Previously seen filter.')

def deltaTimer(dateRec=datetime.date.today(), firstDate=datetime.date.today()):
    options = [0, 2, 6, 12, 18, 24, 30]
    months = round(int((dateRec - firstDate).days) / 30)
    delta = min(options, key=lambda x:abs(x-months))
    return delta


# if __name__ == '__main__':
#     main()
#     sys.exit()