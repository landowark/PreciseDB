# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 10:35:06 2015

This will hold all of the MongoDB convenience functions for this project.

@author: landon
"""

import pymongo as mng
from pymongo.errors import OperationFailure
import jsonpickle
import json
from bson.json_util import loads
import logging
import sqlite3
import os

from matplotlib import dates as mdates

logger = logging.getLogger("Flask.mongo")

def getSecrets():
    file = os.path.abspath(os.path.relpath("keys.json"))
    with open(file, 'r') as f:
        secrets = json.load(f)
    return secrets

def getPatientDB(user="", pwd=""):
    if user == "":
        db = mng.MongoClient().precise_actual.patient
    else:
        db = mng.MongoClient('mongodb://%s:%s@127.0.0.1' % (
            user, pwd)).precise_actual.patient
    return db

def getPatientList():
    # Get list of all patients in mongoDB
    secrets = getSecrets()
    try:
        db = mng.MongoClient('mongodb://%s:%s@127.0.0.1' % (secrets['MONGO_DB_USER'], secrets['MONGO_DB_PASSWORD'])).precise_actual
        patient_list = [doc['_id'] for doc in db.patient.find().batch_size(10)]
    except OperationFailure:
        logger.debug("getPatientList: Can't log in to mongo, attempting userless operation.")
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
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = jsonpickle.encode(newPat)
        db.insert_one(loads(doc))
    except OperationFailure:
        logger.debug("addPatient: Can't log in to mongo, attempting userless operation.")
        db = getPatientDB()
        doc = jsonpickle.encode(newPat)
        db.insert_one(loads(doc))

def getFirstSampleDate(input_pat):
    import datetime
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        nb_patient = db.find_one({"_id":input_pat})
    except OperationFailure:
        db = getPatientDB()
        nb_patient = db.find_one({"_id": input_pat})
    filters = nb_patient['filters']
    print(nb_patient)
    date = min([datetime.datetime.strptime(nb_patient['DateRec'], "%Y-%m-%d").date() for item in filters])
    return(date)

def filterExists(patientNumber, filterNumber):
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        docu = db.find_one({'_id':patientNumber})
    except OperationFailure:
        db = getPatientDB()
        docu = db.find_one({'_id': patientNumber})
    for item in docu['filters']:
        if item == filterNumber:
            return(True)
        else:
            continue
    return(False)

def retrieveAll():
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = {"#" + str(doc['patient_num']).zfill(3) + " " + doc['_id']: doc for doc in db.find()}
        for item in doc:
            doc[item].pop('_id')
            for filter in list(doc[item]['filters'].keys()):
                doc[item]['filters'][filter]['images'] = len(doc[item]['filters'][filter]['images'])
    except OperationFailure:
        logger.debug("retrieveAll: Can't log in to mongo, attempting userless operation.")
        db = getPatientDB()
        doc = {"#" + str(doc['patient_num']).zfill(3) + " " + doc['_id']:doc for doc in db.find()}
        for item in doc:
            doc[item].pop('_id')
    return (doc)
        
def retrieveDoc(patientNumber):
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        logger.debug("retrieveDoc: Can't log in to mongo, attempting userless operation.")
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
    return(doc)
    
def shoveDoc(dicto):
    secrets = getSecrets()

    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = jsonpickle.encode(dicto, unpicklable=False)
        db.find_one_and_replace({'_id': dicto['_id']}, loads(doc))
    except OperationFailure as e:
        logger.debug("shoveDoc: Can't log in to mongo, attempting userless operation.")
        logger.debug(e)
        db = getPatientDB()
        doc = jsonpickle.encode(dicto, unpicklable=False)
        db.find_one_and_replace({'_id':dicto['_id']}, loads(doc))

def updateDateProcessed(patientNumber, filterNumber, input_processed):
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
    for idx, filt in enumerate(doc['filters']):
        if filterNumber in filt['_id']:
            filt['DatePro'] = input_processed
            doc['filters'][idx] = filt
    doc = jsonpickle.encode(doc)
    db.find_one_and_replace({'_id': patientNumber}, loads(doc))

def updateDateImaged(patientNumber, filterNumber, input_imaged):
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
    for idx, filt in enumerate(doc['filters']):
        if filterNumber in filt['_id']:
            filt['DateIm'] = input_imaged
            doc['filters'][idx] = filt
    doc = jsonpickle.encode(doc)
    db.find_one_and_replace({'_id': patientNumber}, loads(doc))

def get_timepoints(patientNumber):
    # Get timepoints obtained for patient
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
    return sorted([doc['filters'][xx]['tPoint'] for xx in [yy for yy in doc['filters'].keys()]])

def timePointExists(patientNumber, tPoint):
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
    tList = sorted([doc['filters'][xx]['tPoint'] for xx in [yy for yy in doc['filters'].keys()]])
    if tPoint in tList:
        return True
    else:
        return False

def get_filter_by_tPoint(patientNumber, tPoint):
    # Get filter by timepoint
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
    for filter in list(doc['filters'].keys()):
        if doc['filters'][filter]['tPoint'] == tPoint:
            filtDict = doc['filters'][filter]
    return(filtDict)

def get_filter_by_number(patientNumber, filterNumber):
    # Get filter by filter number
    secrets = getSecrets()
    try:
        db = getPatientDB(user=secrets['MONGO_DB_USER'], pwd=secrets['MONGO_DB_PASSWORD'])
        doc = db.find_one({'_id': patientNumber})
    except OperationFailure:
        db = getPatientDB()
        doc = db.find_one({'_id': patientNumber})
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
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3"))
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
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3"))
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
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3"))
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

def getAllFilters():
    allFilters = [item for sublist in [list(retrieveDoc(patNum)['filters'].keys()) for patNum in getPatientList()] for
                  item in sublist]
    return allFilters

def getClosestFilterMatches(input_filterNum):
    import difflib
    patientList = getPatientList()
    allFilters = getAllFilters()
    return difflib.get_close_matches(input_filterNum, allFilters, 3)

def getPatientByFilter(filterNum):
    patientList = [patient for patient in getPatientList() if filterNum in list(retrieveDoc(patient)['filters'].keys())]
    return patientList

def getAllNotJanine():
    janine_did = []
    for patient in getPatientList():
        for filter in retrieveDoc(patient)['filters'].keys():
            if 'janine' in retrieveDoc(patient)['filters'][filter].keys():
                janine_did.append(patient)
    janine_didnot = [item for item in getPatientList() if item not in janine_did]
    return janine_didnot


def getFiltersInPatient(patient_num):
    try:
        filters = retrieveDoc(patient_num)['filters'].keys()
    except TypeError:
        filters = []
    if filters == None:
        filters = []
        return filters
    else:
        return list(filters)
