import pandas as pd
import numpy as np
import itertools
from MongoInterface import mongo as mng
import os
import logging

'''
Take a mongo entry for a filter and return a pandas dataframe representing a summary of a filter
'''

logging.basicConfig(filename="C:\\Users\\Landon\\Desktop\\telolog.log", format='%(asctime)s %(message)s', level=logging.INFO)


def ints_from_filter(filter_dict):
    images = filter_dict['images']
    intensities_all = [[images[image]['telomeres'][telo]['int'] for telo in images[image]['telomeres'].keys()] for image in
                   images.keys()]
    intensities_single = list(itertools.chain.from_iterable(intensities_all))
    max_bin = round(np.max(intensities_single), -3)
    bins = np.arange(0, max_bin+1000, 1000)
    intensity_bins = np.histogram(intensities_single, bins)
    bins_data = pd.DataFrame(intensity_bins[0], bins[:-1], columns=['Number of Telomeres'])
    int_single_data = pd.DataFrame(intensities_single)
    int_all_data = pd.DataFrame([np.asarray(item).transpose() for item in intensities_all]).transpose()
    #int_all_data = int_all_data.transpose
    return(bins_data, int_single_data, int_all_data)

def ac_from_filter(filter_dict):
    images = filter_dict['images']
    ac_all = [images[image]['ACRatio'] for image in images.keys()]
    ac_data = pd.DataFrame(ac_all)
    return ac_data

def misc_from_filter(filter_dict):
    images = filter_dict['images']
    numSignals = [images[image]['sigNum'] for image in images.keys()]
    aggs_all = [sum([images[image]['telomeres'][telo]['agg'] for telo in images[image]['telomeres'].keys()]) for image
                in images.keys()]
    ac_all = [images[image]['ACRatio'] for image in images.keys()]
    meanIntall_all = [images[image]['meanIntAll'] for image in images.keys()]
    totalInt_all = [sum([images[image]['telomeres'][telo]['int'] for telo in images[image]['telomeres'].keys()]) for image
                in images.keys()]
    vol_all = [images[image]['nucVol'] for image in images.keys()]
    big_data = list(zip(numSignals, aggs_all, ac_all, meanIntall_all, totalInt_all, vol_all))
    misc_data = pd.DataFrame(big_data, columns=['Total # of signals', 'Total # of aggregates', 'a/c ratio',	'Av.Int. all signals', 'Total intensity', 'Nuclear volume'])
    return misc_data

def get_original_timepoint(patientNumber, filterNumber):
    direc = "C:\\Users\\Landon\\ownCloud\\Documents\\Student Work\\Data\\" + patientNumber
    thing = [x for x in os.listdir(direc) if filterNumber in x]
    print(thing)
    try:
        rel_directory = os.path.basename(thing[0])
    except IndexError:
        logging.warning("Could not find original directory in {p} for {f}".format(p=direc, f=filterNumber))
        return
    original_timepoint = rel_directory.split(" ")[1]
    return original_timepoint

def telomgraph(filter, filePath):

    try:
        bins_data, int_single_data, int_all_data = ints_from_filter(filter)
        ac_data = ac_from_filter(filter)
        misc_data = misc_from_filter(filter)
        writer = pd.ExcelWriter(filePath)
        misc_data.to_excel(writer, 'Sheet3')
        int_all_data.to_excel(writer, 'All Intensities', header=False, index=False)
        int_single_data.to_excel(writer, 'Intensities Single', header=False, index=False)
        ac_data.to_excel(writer, 'a2c-ratio', header=False, index=False)
        logging.debug("Attempting to save telomgraph to " + filePath)
        try:
            writer.save()
        except FileNotFoundError:
            logging.warning("{f} not found, attempting to create.".format(f=filePath))
            os.makedirs(os.path.dirname(filePath))
            writer.save()
    except ValueError as e:
        logging.error("Warning value error for: " + os.path.basename(filePath))
        print(e)

if __name__ == "__main__":

    for patient in mng.getPatientList():
        patient_doc = mng.retrieveDoc(patient)
        patientNumber = patient_doc['_id']
        for filterNumber in [filter for filter in patient_doc['filters'].keys()]:
            print(patientNumber, filterNumber)
            filter = patient_doc['filters'][filterNumber]
            dirpath = os.path.join("C:\\Users\\Landon\\Desktop\\Quon Prostate", patientNumber)
            try:
                oTime = get_original_timepoint(patientNumber, filterNumber)
            except FileNotFoundError:
                continue
            filePath = dirpath + "\\{p} {t} {f}".format(p=patientNumber, f=filterNumber, t=oTime) + '.xlsx'
            print(filePath)
            if not os.path.isfile(filePath):
                telomgraph(filter, filePath)