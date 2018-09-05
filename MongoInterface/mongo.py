# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 10:35:06 2015

This will hold all of the MongoDB convenience functions for this project.

@author: landon
"""

import pymongo as mng
import jsonpickle
from bson.json_util import loads
import logging

logger = logging.getLogger("mainUI.mongo")

def getPatientList():
    # Get list of all patients in mongoDB
    db = mng.MongoClient().prostate_actual
    patient_list = [doc['_id'] for doc in db.patient.find().batch_size(10)]
    return patient_list

def patientExists(input_string):
    # Returns True if patient exists
    db = mng.MongoClient().prostate_actual
    patient_list = getPatientList()
    if input_string in patient_list:
        return(True)
    else:
        return(False)
        
def addPatient(newPat):
    # Takes patient class and inserts into prostate_actual
    db = mng.MongoClient().prostate_actual.patient
    doc = jsonpickle.encode(newPat)
    db.insert_one(loads(doc))

def getFirstSampleDate(input_pat):
    import datetime
    db = mng.MongoClient().prostate_actual.patient
    nb_patient = db.find_one({"_id":input_pat})
    filters = nb_patient['filters']
    print(filters)
    date = min([datetime.datetime.strptime(filters[item]['DateRec'], "%Y-%m-%d").date() for item in filters])
    return(date)

def filterExists(patientNumber, filterNumber):
    db = mng.MongoClient().prostate_actual.patient
    docu = db.find_one({'_id':patientNumber})
    for item in docu['filters']:
        if item == filterNumber:
            return(True)
        else:
            continue
    return(False)
        
def retrieveDoc(patientNumber):
    db = mng.MongoClient().prostate_actual.patient
    doc = db.find_one({"_id":patientNumber})
    return(doc)
    
def shoveDoc(dicto):
    db = mng.MongoClient().prostate_actual.patient
    doc = jsonpickle.encode(dicto, unpicklable=False)
    #doc = dicto
    db.find_one_and_replace({'_id':dicto['_id']}, loads(doc))

def updateDateProcessed(patientNumber, filterNumber, input_processed):
    db = mng.MongoClient().prostate_actual.patient
    docu = db.find_one({'_id': patientNumber})
    for idx, filt in enumerate(docu['filters']):
        if filterNumber in filt['_id']:
            filt['DatePro'] = input_processed
            docu['filters'][idx] = filt
    doc = jsonpickle.encode(docu)
    db.find_one_and_replace({'_id': patientNumber}, loads(doc))

def updateDateImaged(patientNumber, filterNumber, input_imaged):
    db = mng.MongoClient().prostate_actual.patient
    docu = db.find_one({'_id': patientNumber})
    for idx, filt in enumerate(docu['filters']):
        if filterNumber in filt['_id']:
            filt['DateIm'] = input_imaged
            docu['filters'][idx] = filt
    doc = jsonpickle.encode(docu)
    db.find_one_and_replace({'_id': patientNumber}, loads(doc))

def get_timepoints(patientNumber):
    # Get timepoints obtained for patient
    db = mng.MongoClient().prostate_actual.patient
    doc = db.find_one({"_id": patientNumber})
    return sorted([doc['filters'][xx]['tPoint'] for xx in [yy for yy in doc['filters'].keys()]])

def timePointExists(patientNumber, tPoint):
    db = mng.MongoClient().prostate_actual.patient
    doc = db.find_one({"_id": patientNumber})
    tList = sorted([doc['filters'][xx]['tPoint'] for xx in [yy for yy in doc['filters'].keys()]])
    if tPoint in tList:
        return True
    else:
        return False

def get_filter_by_tPoint(patientNumber, tPoint):
    # Get filter by timepoint
    db = mng.MongoClient().prostate_actual.patient
    doc = db.find_one({"_id": patientNumber})
    filtDict = {}
    for filter in list(doc['filters'].keys()):
        if doc['filters'][filter]['tPoint'] == tPoint:
            filtDict[filter] = doc['filters'][filter]
    return(filtDict)

def get_filter_by_number(patientNumber, filterNumber):
    # Get filter by filter number
    db = mng.MongoClient().prostate_actual.patient
    doc = db.find_one({"_id": patientNumber})
    filtDict = doc['filters'][filterNumber]
    return(filtDict)

def get_timepoint_for_all(timepoint="+00m"):
    timepoints = {}
    patients = [retrieveDoc(patient) for patient in getPatientList()]
    for patient in patients:
        filts = list(patient['filters'].keys())
        for filter in filts:
            if patient['filters'][filter]['tPoint'] == timepoint:
                timepoints[patient['_id']] = patient['filters'][filter]
    return timepoints
