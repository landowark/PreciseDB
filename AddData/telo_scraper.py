# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:33:31 2015

This module will scrape teloview data out of all folders in given directory"

@author: Landon
"""

from Classes import filterizer as flz, patientizer as ptz, imagizer as imz, namer
from DB_DIR import menu_items as fg, mongo as mng
import sys
import os
from glob import glob
import logging

#set up logging.
logger = logging.getLogger("Flask.teloscrape")

def scrape_dir(directory):
    # recur find in UI.menu_items finds all xlsx files in directories
    file_list = fg.recur_find(directory, 'xlsx')
    # include files containing 'deconvolution' and not containing 'lymp'
    # file_list = [item for item in file_list if 'deconvolution' in item and 'lymp' not in item]
    try:
        # Ensure there are at least 30 files
        assert len(file_list) >= 30
        # Crop number of files to the first 30.
        file_list = file_list[0:30]
    except AssertionError:
        logger.warning("{q}: Not enough cells for analysis.".format(q=directory))
        file_list = file_list
    print(file_list)
    # enforce patient number scheme using Classes.namer
    patientNumber = namer.parsePatient(file_list[1])
    # enforce filter number scheme using Classes.namer
    filterNumber = namer.parseFilter(file_list[1])
    logger.debug("Patient Number: %s Filter Number: %s" % (patientNumber, filterNumber))
    # check if patient exists
    if mng.patientExists(patientNumber) == False:
        logger.debug('Previously unseen patient {s}. Adding to database.'.format(s=patientNumber))
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
        logger.warning("%s - %s Filter not found, skipping." % (patientNumber, filterNumber))
    try:
        # Attempt to get filter received date from record
        newFilt.DateRec = \
        [patientDoc['filters'][item]['DateRec'] for item in patientDoc['filters'] if item == filterNumber][0]
    except (KeyError, IndexError):
        # If no record this will default to tPoint="+00m" as in Classes.filterizer
        logger.warning("No date found!")
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
    # Set this filter's images to dictionary
    newFilt.images = dict_images
    # Calculate means, percentages, etc. in filter
    newFilt.data_calc()
    this_filter = newFilt.jsonable()
    # ensure filter number matches filter in patient before assigning.
    for item in patientDoc['filters']:
        if item == filterNumber:
            logger.debug("Hit " + filterNumber)
            patientDoc['filters'][item] = this_filter
    # update patient
    mng.shoveDoc(patientDoc)
    logger.debug("Done!")


if __name__ == '__main__':
    # main will scrape all existing teloview files.
    # set path
    pathName = input("Input the main data directory: ")  # main dir for project data.
    # get all dirs containing files with 'deconvolution' and 'CTC' in the path name
    result = [y for x in os.walk(pathName) for y in glob(os.path.join(x[0], '*.xlsx')) if
              'deconvolution' in y and 'CTC' in y]
    # get unique dirs only.
    dirs = set([os.path.dirname(filename) for filename in result])
    sorted(dirs)
    for directory in dirs:
        logging.debug("Starting " + directory)
        scrape_dir(directory)
    # use chartmaker main to remake charts automatically
    sys.exit()