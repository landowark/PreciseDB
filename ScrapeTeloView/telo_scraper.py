# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:33:31 2015

@author: Landon
"""

''' TODO: has to find the appropriate filter and 
            return as a dict{}, then pop in the scraped values'''

from Classes import filterizer as flz, patientizer as ptz, imagizer as imz, namer
from UI import menu_items as fg
from MongoInterface import mongo as mng
from ScrapeTeloView import chart_maker_main as chm, telomgraph_emulator as te
import sys
import os
from glob import glob
import logging

logging.basicConfig(filename="C:\\Users\\Landon\\Desktop\\telolog.log", format='%(asctime)s %(message)s', level=logging.INFO)


def main():

    pathName = "C:\\Users\\Landon\\Dropbox\\Documents\\Student Work\\Data" # main dir for project data.
    result = [y for x in os.walk(pathName) for y in glob(os.path.join(x[0], '*.xlsx')) if 'deconvolution' in y and 'CTC' in y]
    dirs = set([os.path.dirname(filename) for filename in result])
    sorted(dirs)
    for directory in dirs:
        logging.debug("Starting " + directory)
        split_dir = directory.split("\\")
        file_list = fg.recur_find(directory, 'xlsx')
        file_list = [item for item in file_list if 'deconvolution' in item and 'lymp' not in item]
        try:
            assert len(file_list) >= 30
            file_list = file_list[0:30]
        except:
            logging.warning("{q}: Not enough cells for analysis.".format(q=directory))
            continue
        patientNumber = namer.parsePatient(file_list[1])
        filterNumber = namer.parseFilter(file_list[1])
        logging.debug("Patient Number: %s Filter Number: %s" %(patientNumber, filterNumber))
        if mng.patientExists(patientNumber) == False:
            logging.debug('Previously unseen patient {s}. Adding to database.'.format(s=patientNumber))
            newPat = ptz.Patient(patNum=patientNumber)
            mng.addPatient(newPat)
            # This will create a new filter based on info scraped from filepath.
        # retrieve mongodb patient doc
        patientDoc = mng.retrieveDoc(patientNumber)
        try:
            newFilt = flz.Filter(tPoint=patientDoc['filters'][filterNumber]['tPoint'])
        except KeyError:
            logging.warning("%s - %s Filter not found, skipping." % (patientNumber, filterNumber))
            continue
        try:
            # Attempt to get filter received date from record
            newFilt.DateRec = [patientDoc['filters'][item]['DateRec'] for item in patientDoc['filters'] if item == filterNumber][0]
        except (KeyError, IndexError):
        #     # If no record ask for date.
             logging.warning("No date found!")
        dict_images = {}
        for item in file_list:
            name = imz.Image().name_scrape(item)
            new_image = imz.Image()
            new_image.data_scrape(item)
            new_image = new_image.jsonable()
            dict_images[name] = new_image
            # try:
            #     shutil.copy(item, os.path.join(desktop_dir, os.path.basename(item)))
            # except FileNotFoundError:
            #     os.makedirs(desktop_dir)
            #     shutil.copy(item, os.path.join(desktop_dir, os.path.basename(item)))
        newFilt.images = dict_images
        newFilt.data_calc()
        this_filter = newFilt.jsonable()
        desktop_dir = os.path.join("C:\\Users\\Landon\\Desktop\\Quon Prostate", patientNumber + "PR", split_dir[-2])
        for item in patientDoc['filters']:
            if item == filterNumber:
                logging.debug("Hit " + filterNumber)
                patientDoc['filters'][item] = this_filter
        te.telomgraph(dict(newFilt.jsonable()), desktop_dir + '.xlsx')
        mng.shoveDoc(patientDoc)
    #use chartmaker main to remake charts automatically
    chm.main()
    sys.exit()

if __name__ == '__main__':
    main()