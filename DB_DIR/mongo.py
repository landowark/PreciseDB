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
import sqlite3
import os

from matplotlib import dates as mdates

logger = logging.getLogger("mainUI.mongo")

def getPatientList():
    # Get list of all patients in mongoDB
    db = mng.MongoClient().precise_actual
    patient_list = [doc['_id'] for doc in db.patient.find().batch_size(10)]
    return patient_list

def patientExists(input_string):
    # Returns True if patient exists
    patient_list = getPatientList()
    if input_string in patient_list:
        return(True)
    else:
        return(False)
        
def addPatient(newPat):
    # Takes patient class and inserts into precise_actual
    db = mng.MongoClient().precise_actual.patient
    doc = jsonpickle.encode(newPat)
    db.insert_one(loads(doc))

def getFirstSampleDate(input_pat):
    import datetime
    db = mng.MongoClient().precise_actual.patient
    nb_patient = db.find_one({"_id":input_pat})
    filters = nb_patient['filters']
    print(filters)
    date = min([datetime.datetime.strptime(filters[item]['DateRec'], "%Y-%m-%d").date() for item in filters])
    return(date)

def filterExists(patientNumber, filterNumber):
    db = mng.MongoClient().precise_actual.patient
    docu = db.find_one({'_id':patientNumber})
    for item in docu['filters']:
        if item == filterNumber:
            return(True)
        else:
            continue
    return(False)
        
def retrieveDoc(patientNumber):
    db = mng.MongoClient().precise_actual.patient
    doc = db.find_one({"_id":patientNumber})
    return(doc)
    
def shoveDoc(dicto):
    db = mng.MongoClient().precise_actual.patient
    doc = jsonpickle.encode(dicto, unpicklable=False)
    #doc = dicto
    db.find_one_and_replace({'_id':dicto['_id']}, loads(doc))

def updateDateProcessed(patientNumber, filterNumber, input_processed):
    db = mng.MongoClient().precise_actual.patient
    docu = db.find_one({'_id': patientNumber})
    for idx, filt in enumerate(docu['filters']):
        if filterNumber in filt['_id']:
            filt['DatePro'] = input_processed
            docu['filters'][idx] = filt
    doc = jsonpickle.encode(docu)
    db.find_one_and_replace({'_id': patientNumber}, loads(doc))

def updateDateImaged(patientNumber, filterNumber, input_imaged):
    db = mng.MongoClient().precise_actual.patient
    docu = db.find_one({'_id': patientNumber})
    for idx, filt in enumerate(docu['filters']):
        if filterNumber in filt['_id']:
            filt['DateIm'] = input_imaged
            docu['filters'][idx] = filt
    doc = jsonpickle.encode(docu)
    db.find_one_and_replace({'_id': patientNumber}, loads(doc))

def get_timepoints(patientNumber):
    # Get timepoints obtained for patient
    db = mng.MongoClient().precise_actual.patient
    doc = db.find_one({"_id": patientNumber})
    return sorted([doc['filters'][xx]['tPoint'] for xx in [yy for yy in doc['filters'].keys()]])

def timePointExists(patientNumber, tPoint):
    db = mng.MongoClient().precise_actual.patient
    doc = db.find_one({"_id": patientNumber})
    tList = sorted([doc['filters'][xx]['tPoint'] for xx in [yy for yy in doc['filters'].keys()]])
    if tPoint in tList:
        return True
    else:
        return False

def get_filter_by_tPoint(patientNumber, tPoint):
    # Get filter by timepoint
    db = mng.MongoClient().precise_actual.patient
    doc = db.find_one({"_id": patientNumber})
    for filter in list(doc['filters'].keys()):
        if doc['filters'][filter]['tPoint'] == tPoint:
            filtDict = doc['filters'][filter]
    return(filtDict)

def get_filter_by_number(patientNumber, filterNumber):
    # Get filter by filter number
    db = mng.MongoClient().precise_actual.patient
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

def store_psa_maximum():
    # A function for storing the maximum of psa which is used for set axes when plotting.
    psas = [item for patient_values in [list(retrieveDoc(patient)['PSAs'].values()) for patient in getPatientList()] for item in patient_values]
    maximum = max(psas)
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.sqlite"))
    cursor = conn.cursor()

    cursor.execute('''SELECT maximum FROM maximums WHERE para_name=?''', ("PSA"))
    oldMax = cursor.fetchone()
    if oldMax < maximum:
        cursor.execute('''UPDATE maximums SET maximum = ? WHERE id = ? ''', (maximum, "PSA"))
    conn.commit()
    conn.close()

def store_parameter_maximum(parameter_name):
    # A function for storing the maximum of each nuclear parameter which is used for set axes when plotting.
    para = []
    for patient in [retrieveDoc(patient) for patient in getPatientList()]:
        try:
            measures = [patient['filters'][filter][parameter_name] for filter in patient['filters'].keys()]
            for item in measures:
                para.append(item)
        except KeyError:
            continue
    maximum = max(para)
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.sqlite"))
    cursor = conn.cursor()
    cursor.execute('''SELECT maximum FROM maximums WHERE para_name=?''', (parameter_name))
    oldMax = cursor.fetchone()
    if oldMax < maximum:
        cursor.execute('''UPDATE maximums SET maximum = ? WHERE id = ? ''', (maximum, parameter_name))
    conn.commit()
    conn.close()

def get_all_parameters():
    para = []
    for patient in [retrieveDoc(patient) for patient in getPatientList()]:
        try:
            measures = [patient['filters'][filter].keys() for filter in patient['filters'].keys()]
            for item in measures:
                for thing in list(item):
                    if thing not in para and thing not in ['images', 'tPoint', 'DateRec', 'CTCNum']:
                        para.append(thing)
        except KeyError:
            continue
    return para

def get_parameter_maximum(parameter_name):
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.sqlite"))
    cursor = conn.cursor()
    cursor.execute('''SELECT maximum FROM maximums WHERE para_name=?''', (parameter_name,)) # note, the comma is necessary for the sql syntax
    oldMax = cursor.fetchone()[0]
    conn.close()
    return oldMax

def getTreatments(patient_number):
    treatments = retrieveDoc(patient_number)['treatments']
    trx_dates = []
    for item in treatments.keys():
        try:
            dicto = {}
            dicto['start'] = mdates.datestr2num(item)
            dicto['end'] = mdates.datestr2num(treatments[item]['End Date'])
            dicto['name'] = treatments[item]['Treatment']
            trx_dates.append(dicto)
        except ValueError:
            del dicto
            continue
    return trx_dates