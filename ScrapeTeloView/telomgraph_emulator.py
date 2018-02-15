import pandas as pd
import numpy as np
import itertools
from MongoInterface import mongo as mng
import os
import logging

'''
Take a mongo entry for a filter and return a pandas dataframe representing a summary of a filter
'''

logger = logging.getLogger("mainUI.telomgraph")


def ints_from_filter(filter_dict):
    # gets intensity data.
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
    # get list of signal counts per image
    numSignals = [images[image]['sigNum'] for image in images.keys()]
    # get image keys and for each one get telomere keys for it and for each of those get if telomere is aggregate, sum
    aggs_all = [sum([images[image]['telomeres'][telo]['agg'] for telo in images[image]['telomeres'].keys()]) for image
                in images.keys()]
    # get list of ac_ratios per filter
    ac_all = [images[image]['ACRatio'] for image in images.keys()]
    # get list of mean Intensities per filter
    meanIntall_all = [images[image]['meanIntAll'] for image in images.keys()]
    # get list of total intensities per filter
    totalInt_all = [sum([images[image]['telomeres'][telo]['int'] for telo in images[image]['telomeres'].keys()]) for image
                in images.keys()]
    # get list of nuclear volumes per filter
    vol_all = [images[image]['nucVol'] for image in images.keys()]
    # combine all the lists above.
    big_data = list(zip(numSignals, aggs_all, ac_all, meanIntall_all, totalInt_all, vol_all))
    # create dataframe.
    misc_data = pd.DataFrame(big_data, columns=['Total # of signals', 'Total # of aggregates', 'a/c ratio',	'Av.Int. all signals', 'Total intensity', 'Nuclear volume'])
    return misc_data

def get_original_timepoint(patientNumber, filterNumber):
    direc = "C:\\Users\\Landon\\Dropbox\\Documents\\Student Work\\Data\\" + patientNumber
    thing = [x for x in os.listdir(direc) if filterNumber in x]
    print(thing)
    try:
        rel_directory = os.path.basename(thing[0])
    except IndexError:
        logging.warning("Could not find original directory in {p} for {f}".format(p=direc, f=filterNumber))
        return
    original_timepoint = rel_directory.split(" ")[1]
    return original_timepoint

def intChartMaker(data, workbook, sampleName):
    bin_values = pd.DataFrame(data.index.values, columns=['bins'])
    bin250labels = bin_values['bins']

    bin250max = bin250labels[pd.notnull(bin250labels)].idxmax()
    print(bin250max)
    bin250chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
    bin250chart.add_series({
        'categories': ['bins', 1, 0, bin250max, 0],
        'values': ['bins', 1, 1, bin250max, 1],
        'line': {'color': 'red'},
        'marker': {'type': 'diamond', 'border': {'color': 'red'}, 'fill': {'color': 'red'}, }
    })
    bin250chart.set_x_axis({
        'name': 'Intensity[a.u.]',
        'name_font': {'size': 14, 'bold': True},
    })
    bin250chart.set_y_axis({
        'name': 'Number of Telomeres',
        'name_font': {'size': 14, 'bold': True},
    })
    bin250chart.set_title({'name': sampleName})
    bin250chart.set_legend({'none': True})
    bin250chartsheet = workbook.add_chartsheet()
    bin250chartsheet.set_chart(bin250chart)

def telomgraph(patient_number, filter_number, filePath):
    filter = mng.get_filter_by_number(patient_number, filter_number)
    sampleName = os.path.basename(filePath)
    logger.info("Telomgraph module reporting in for %s." % sampleName)
    try:
        bins_data, int_single_data, int_all_data = ints_from_filter(filter)
        ac_data = ac_from_filter(filter)
        misc_data = misc_from_filter(filter)
        misc_data.index += 1
        writer = pd.ExcelWriter(filePath)
        workbook = writer.book
        misc_data.to_excel(writer, 'Sheet3')
        int_all_data.to_excel(writer, 'All Intensities', header=False, index=False)
        int_single_data.to_excel(writer, 'Intensities Single', header=False, index=False)
        ac_data.to_excel(writer, 'a2c-ratio', header=False, index=False)
        bins_data.to_excel(writer, 'bins')
        # TODO insert charts into workbook. See scrapeexcel in Inspiration
        # try:
        intChartMaker(bins_data, workbook, sampleName)
        # except Exception as e:
        #     print("Problem with chart maker: %s" % e)
        logger.debug("Attempting to save telomgraph to " + filePath)
        try:
            writer.save()
        except FileNotFoundError:
            logger.warning("{f} not found, attempting to create.".format(f=filePath))
            os.makedirs(os.path.dirname(filePath))
            writer.save()
    except ValueError as e:
        logger.error("Warning value error for: %s %s" % (os.path.basename(filePath), e))

if __name__ == "__main__":
    telomgraph("MB0393PR", "13AA8517", "C:\\Users\\Landon\\\Desktop\\test.xlsx")


    # for patient in mng.getPatientList():
    #     patient_doc = mng.retrieveDoc(patient)
    #     patientNumber = patient_doc['_id']
    #     for filterNumber in [filter for filter in patient_doc['filters'].keys()]:
    #         print(patientNumber, filterNumber)
    #         filter = patient_doc['filters'][filterNumber]
    #         dirpath = os.path.join("C:\\Users\\Landon\\Desktop\\Quon Prostate", patientNumber)
    #         try:
    #             oTime = get_original_timepoint(patientNumber, filterNumber)
    #         except FileNotFoundError:
    #             continue
    #         filePath = dirpath + "\\{p} {t} {f}".format(p=patientNumber, f=filterNumber, t=oTime) + '.xlsx'
    #         print(filePath)
    #         if not os.path.isfile(filePath):
    #             telomgraph(filter, filePath)