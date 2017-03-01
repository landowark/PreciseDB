# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 10:35:06 2015

This will hold all of the MongoDB functions for this project.

@author: landon
"""

import pymongo as mng
import jsonpickle
import bson
from bson.json_util import loads

def findPatient(input_string):
    db = mng.MongoClient().prostate_actual
    patient_list = []
    for doc in db.patient.find():
        patient_list.append(doc['_id'])
    if input_string in patient_list:
        return(True)
    else:
        return(False)
        
def addPatient(newPat):
    db = mng.MongoClient().prostate_actual.patient
    doc = jsonpickle.encode(newPat)
    db.insert_one(loads(doc))

def findFilter(patientNumber, filterNumber):
    db = mng.MongoClient().prostate_actual.patient
    docu = db.find_one({'_id':patientNumber})
    if 'Filter_' + filterNumber in docu.keys():
        return(True)
    else:
        return(False)
        
def retrieveDoc(patientNumber):
    db = mng.MongoClient().prostate_actual.patient
    doc = db.find_one({'_id':patientNumber})
    return(doc)
    
def shoveDoc(dicto):
    db = mng.MongoClient().prostate_actual.patient
    doc = jsonpickle.encode(dicto)
    db.find_one_and_replace({'_id':dicto['_id']}, loads(doc))