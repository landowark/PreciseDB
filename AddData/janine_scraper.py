
import pandas as pd
from xlrd.biffh import XLRDError
from Classes import namer
from DB_DIR import mongo as mng
import difflib
import numpy as np

# step one open file and create dataframe
def openFileAndParse(inputFile):
    try:
        data = pd.read_excel(inputFile, "Feuil1")
    except XLRDError:
        data = pd.read_excel(inputFile, "Sheet1")
    data.fillna("")
    filters = [filter for filter in data.to_dict(orient='records') if type(filter['Scan Number']) != float]
    return filters

def makeLists(filters: list):
    # split filters into two lists, ones that have exact matches in DB and ones that don't.
    filterCheck = []
    matchesDB = []
    notinDB = []
    allFilters = mng.getAllFilters()
    for filter in filters:
        try:
            filter.pop("Date ")
        except KeyError:
            filter.pop("Date")
        try:
            filter['Scan Number'] = namer.parseFilter(filter['Scan Number'])
            filterCheck.append(filter)
        except:
            notinDB.append(filter)
    for filter in filterCheck:
        if filter['Scan Number'] in allFilters:
            matchesDB.append(filter)
        else:
            notinDB.append(filter)
    return matchesDB, notinDB

def addJanineData(filter: dict):

    if type(filter[' Comments']) == float:
        filter[' Comments'] = ""
    filterNum = filter.pop('Scan Number')
    #print(filterNum)
    patient = mng.getPatientByFilter(filterNum)[0]
    #print(patient)
    doc = mng.retrieveDoc(patient)
    doc['filters'][filterNum]['janine'] = filter
    mng.shoveDoc(doc)

def addChoicesToDict(notInDB: dict):
    allFilts = mng.getAllFilters()
    notInDB['choices'] = [""] + difflib.get_close_matches(notInDB['Scan Number'], allFilts, 3)
    return notInDB