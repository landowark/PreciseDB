# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:33:31 2015

This module will scrape teloview data out of all folders in "C:\\Users\\Landon\\Dropbox\\Documents\\Student Work\\Data"

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
from logging.handlers import RotatingFileHandler

#set up logging.
logger = logging.getLogger("teloscrape")
logger.setLevel(logging.DEBUG)
fh = RotatingFileHandler('C:\\Users\\Landon\\Desktop\\Debugging\\QP.log', maxBytes=50000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def scrape_dir(directory):
    try:
        split_dir = directory.split("\\")
        # recur find in UI.menu_items finds all xlsx files in directories
        file_list = fg.recur_find(directory, 'xlsx')
        # include files containing 'deconvolution' and not containing 'lymp'
        file_list = [item for item in file_list if 'deconvolution' in item and 'lymp' not in item]
        try:
            # Ensure there are at least 30 files
            assert len(file_list) >= 30
            # Crop number of files to the first 30.
            file_list = file_list[0:30]
        except AssertionError:
            logging.warning("{q}: Not enough cells for analysis.".format(q=directory))

        # enforce patient number scheme using Classes.namer
        patientNumber = namer.parsePatient(file_list[1])
        # enforce filter number scheme using Classes.namer
        filterNumber = namer.parseFilter(file_list[1])
        logging.debug("Patient Number: %s Filter Number: %s" % (patientNumber, filterNumber))
        # check if patient exists
        if mng.patientExists(patientNumber) == False:
            logging.debug('Previously unseen patient {s}. Adding to database.'.format(s=patientNumber))
            # Create basic patient object
            newPat = ptz.Patient(patNum=patientNumber)
            # Add new patient to DB
            mng.addPatient(newPat)
        # This will create a new filter based on info scraped from filepath.
        # retrieve mongodb patient doc
        patientDoc = mng.retrieveDoc(patientNumber)
        try:
            # Create new basic filter object only if it has already been logged in the DB
            newFilt = flz.Filter(tPoint=patientDoc['filters'][filterNumber]['tPoint'])
        except KeyError:
            logging.warning("%s - %s Filter not found, skipping." % (patientNumber, filterNumber))
        try:
            # Attempt to get filter received date from record
            newFilt.DateRec = \
            [patientDoc['filters'][item]['DateRec'] for item in patientDoc['filters'] if item == filterNumber][0]
        except (KeyError, IndexError):
            # If no record this will default to tPoint="+00m" as in Classes.filterizer
            logging.warning("No date found!")
        # initialize dictionary
        dict_images = {}
        for item in file_list:
            # Parse image name using Classes.namer
            name = namer.parseImage(item)
            # Create new image object, filling in with scraped data and adding to dictionary
            new_image = imz.Image()
            new_image.data_scrape(item)
            new_image = new_image.jsonable()
            dict_images[name] = new_image
            # try:
            #     shutil.copy(item, os.path.join(desktop_dir, os.path.basename(item)))
            # except FileNotFoundError:
            #     os.makedirs(desktop_dir)
            #     shutil.copy(item, os.path.join(desktop_dir, os.path.basename(item)))
        # Set this filter's images to dictionary
        newFilt.images = dict_images
        # Calculate means, percentages, etc. in filter
        newFilt.data_calc()
        this_filter = newFilt.jsonable()
        desktop_dir = os.path.join("C:\\Users\\Landon\\Desktop\\Quon Prostate", patientNumber + "PR", split_dir[-2])
        # ensure filter number matches filter in patient before assigning.
        for item in patientDoc['filters']:
            if item == filterNumber:
                logging.debug("Hit " + filterNumber)
                patientDoc['filters'][item] = this_filter
        # run telomgraph emulator on filter
        # te.telomgraph(dict(newFilt.jsonable()), desktop_dir + '.xlsx')
        # update patient
        print("Done!")
        mng.shoveDoc(patientDoc)
    except Exception as e:
        print(e)

def main():
    # set path
    pathName = "C:\\Users\\Landon\\Dropbox\\Documents\\Student Work\\Data" # main dir for project data.
    # get all dirs containing files with 'deconvolution' and 'CTC' in the path name
    result = [y for x in os.walk(pathName) for y in glob(os.path.join(x[0], '*.xlsx')) if 'deconvolution' in y and 'CTC' in y]
    # get unique dirs only.
    dirs = set([os.path.dirname(filename) for filename in result])
    sorted(dirs)
    for directory in dirs:
        logging.debug("Starting " + directory)
        scrape_dir(directory)
    #use chartmaker main to remake charts automatically
    #chm.main()
    sys.exit()

if __name__ == '__main__':
    main()