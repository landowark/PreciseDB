
import pandas as pd
from xlrd.biffh import XLRDError
from Classes import namer
from DB_DIR import mongo as mng

# step one open file and create dataframe
def openFileAndParse(inputFile):
    try:
        data = pd.read_excel(inputFile, "Feuil1")
    except XLRDError:
        data = pd.read_excel(inputFile, "Sheet1")
    filters = [filter for filter in data.to_dict(orient='records') if type(filter['Scan Number']) != float]
    return filters

def makeLists(filters):
    # split filters into two lists, ones that have exact matches in DB and ones that don't.
    filterCheck = []
    matchesDB = []
    notinDB = []
    allFilters = mng.getAllFilters()
    print(allFilters)
    for filter in filters:
        try:
            filter['Scan Number'] = namer.parseFilter(filter['Scan Number'])
            filterCheck.append(filter['Scan Number'])
        except:
            notinDB.append(filter['Scan Number'])
    for filter in filterCheck:
        if filter in allFilters:
            matchesDB.append(filter)
        else:
            notinDB.append(filter)
    return matchesDB, notinDB

def addJanineData(filterNum, data):
    patient = mng.getPatientByFilter(filterNum)[0]
    doc = mng.retrieveDoc(patient)
    doc['filters'][filterNum]['janine'] = data
    mng.shoveDoc(doc)
