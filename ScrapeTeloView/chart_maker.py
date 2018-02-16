"""
I should probably create a class inheriting from the plt.
I think that's a job for a new python file though.
-- nope Monday - September 25, 2017
"""
from MongoInterface import mongo
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np
import logging
import os
import shutil

logger = logging.getLogger("mainUI.chart_maker")

def createTextBox(patient_number):
    doc = mongo.retrieveDoc(patient_number)
    pDRE = doc['DRE']
    pGleason = doc['procedures'][list(doc['procedures'].keys())[0]]['Gleason']
    pStatus = doc['status']
    pTScore = doc['tScore']
    textstr = 'Status: %s\nDRE: %s\ntScore: %s\nGleason: %s' % (pStatus, pDRE, pTScore, pGleason)
    return(textstr)

def getTreatments(patient_number):
    treatments = mongo.retrieveDoc(patient_number)['treatments']
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


def getFigure(patientnumber="MB0389PR", parametername='meanInt', figPath="C:\\Users\\Landon\\Desktop\\"):
    #try:
        psaDates, psaLevels, parameterDates, parameterLevels, fullDates = calculate_axes(patientnumber, parametername)
        fig, ax1 = plt.subplots()
        fig.set_size_inches(24,12)
        ax1.plot(psaDates, psaLevels, 'r', marker='.')
        ax1.set_xlabel('Date', fontdict={'fontsize':22})
        plt.title(patientnumber, {'fontsize':22})
        # Make the y-axis label, ticks and tick labels match the line color.
        ax1.set_ylabel('PSA level', color='r', fontdict={'fontsize':18})
        ax1.tick_params('y', colors='r')
        plt.xticks(fullDates, [mdates.num2date(x).strftime('%Y-%m-%d') for x in fullDates], rotation=45)

        ax2 = ax1.twinx()
        ax2.plot(parameterDates, parameterLevels, 'b', marker='d')
        ax2.set_ylabel(parametername, color='b', fontdict={'fontsize':18})
        ax2.tick_params('y', colors='b')

        #textbox for patient parameters
        textstr = createTextBox(patientnumber)
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        ax1.text(0.75, 0.55, textstr, transform=ax1.transAxes, fontsize=14,
                verticalalignment='top', bbox=props)

        # add x highlight for treatment
        treatments = getTreatments(patientnumber)
        for trx in treatments:
            try:
                if "Bical" in trx['name']: facecolor = 'blue'
                elif "RT" in trx['name']: facecolor = 'orange'
                elif "Leu" in trx['name']: facecolor = 'red'
                else: facecolor = 'gray'
                bbox_props = dict(boxstyle="square,pad=0.3", fc=facecolor, ec="b", lw=2, alpha=0.7)
                plt.axvspan(trx['start'], trx['end'], facecolor=facecolor, alpha=0.25)
                ax1.text(((trx['start'] + trx['end'])/2), 1, trx['name'], color='white', va="bottom", ha='center', size=15, rotation=90, bbox=bbox_props)
            except ValueError:
                continue

        for label in (ax1.get_xticklabels() + ax1.get_yticklabels()): label.set_fontsize(13)

        # fullPath = os.path.join(figPath, patientnumber + " " + parametername + ".jpg")
        # split_dir = figPath.split("\\")
        # desktop_path = os.path.join("C:\\Users\\Landon\\Desktop\\Quon Prostate", split_dir[-1])
        # fig.tight_layout()
        # fig.savefig(fullPath)
        # shutil.copy(fullPath, desktop_path)
        # plt.close('all')
    # except Exception as e:
    #     print(e)


def calculate_axes(patientnumber, parametername):
    doc = mongo.retrieveDoc(patientnumber)
    psa = list(zip([mdates.datestr2num(item) for item in doc['PSAs'].keys()], [item for item in doc['PSAs'].values()]))
    psa = sorted(psa, key=lambda x: x[0])
    # get data from document
    filters = [item for item in list(doc['filters'].keys())]
    data = list(zip([mdates.datestr2num(doc['filters'][filter]['DateRec']) for filter in filters],
                    [doc['filters'][filter][parametername] for filter in filters]))
    data = sorted(data, key=lambda x: x[0])
    # set dates when samples were taken in
    fullDates = sorted([x[0] for x in psa] + [x[0] for x in data])
    fullDates = list(set(fullDates))
    fullDates = list(np.linspace(min(fullDates), max(fullDates), num=100, endpoint=True))[0::5]
    psaDates = [x[0] for x in psa]
    psaLevels = [y[1] for y in psa]
    parameterDates = [x[0] for x in data]
    parameterLevels = [y[1] for y in data]
    return psaDates, psaLevels, parameterDates, parameterLevels, fullDates

if __name__ == "__main__":
    figure = getFigure("MB0438PR", "meanInt")
    plt.show()
    #plt.close('all')
