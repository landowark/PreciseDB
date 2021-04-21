"""
I should probably create a class inheriting from the plt.
I think that's a job for a new python file though.
-- nope Monday - September 25, 2017
"""
from DB_DIR import mongo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import logging

logger = logging.getLogger("Flask.chart_maker")

def createTextBox(patient_number):
    # Makes a string to display patient values.
    doc = mongo.retrieveDoc(patient_number)
    pDRE = doc['DRE']
    pGleason = doc['procedures'][list(doc['procedures'].keys())[0]]['Gleason']
    pStatus = doc['status']
    pTScore = doc['tScore']
    textstr = 'Status: %s\nDRE: %s\ntScore: %s\nGleason: %s' % (pStatus, pDRE, pTScore, pGleason)
    return(textstr)

def calculate_axes(patientnumber="MB0389PR", parametername="meanInt"):
    # pulls out all the data necessary to make the chart.
    # try:
    doc = mongo.retrieveDoc(patientnumber)
    psa = list(zip([mdates.datestr2num(item) for item in doc['PSAs'].keys()], [item for item in doc['PSAs'].values()]))
    psa = sorted(psa, key=lambda x: x[0])
    # get data from document
    filters = [item for item in list(doc['filters'].keys())]
    # added in if expression to prevent non-analyzed filter from showing up.
    data = list(zip([mdates.datestr2num(doc['filters'][filter]['DateRec']) for filter in filters if len(doc['filters'][filter]['images']) > 0],
                    [doc['filters'][filter][parametername] for filter in filters if len(doc['filters'][filter]['images']) > 0]))
    data = sorted(data, key=lambda x: x[0])
    # set dates when samples were taken in
    fullDates = sorted([x[0] for x in psa] + [x[0] for x in data])
    fullDates = list(set(fullDates))
    fullDates = list(np.linspace(min(fullDates), max(fullDates), num=100, endpoint=True))[0::5]
    print(max(mdates.num2date(fullDates)).strftime("%Y-%m-%d"))
    psaDates = [x[0] for x in psa]
    psaLevels = [y[1] for y in psa]
    parameterDates = [x[0] for x in data]
    parameterLevels = [y[1] for y in data]
    return psaDates, psaLevels, parameterDates, parameterLevels, fullDates
    # except Exception as e:
    #     logger.debug("Exception in calculate axes: ")


def getTrxDates(patientnumber="MB0389PR"):
    return mongo.getTreatments(patientnumber)