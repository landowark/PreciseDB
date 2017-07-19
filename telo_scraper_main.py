# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:33:31 2015

@author: Landon
"""

''' TODO: has to find the appropriate filter and 
            return as a dict{}, then pop in the scraped values'''   

import imagizer as imz
import filterizer as flz
import menu_items as fg
import patientizer as ptz
import namer
import mongo as mng
import lw_calendar as cal #custom calendar widget to choose dates
import sys
from PyQt5 import QtWidgets #for calling QApplication in main (necessary to prevent multiple calls in fxns)

def main():
    # With the addition of my Access scraper, this is kind of defunct
    # I just need to point the excel files to the proper filter
    app = QtWidgets.QApplication.instance()
    # checks if QApplication already exists
    if not app: # create QApplication if it doesnt exist
        app = QtWidgets.QApplication(sys.argv)
    ex = fg.getDir()
    pathName = ex.text
    #pathName = "C:\\Users\\Landon\\Documents\\Student Work\\Data\\MB0389PR\\MB0389 +0m 13AA8592" #placeholder for testing.
    file_list = fg.recur_find(pathName, 'xlsx')
    file_list = [item for item in file_list if 'deconvolution' in item and 'lymp' not in item]
    patientNumber = namer.parsePatient(file_list[1])
    filterNumber = namer.parseFilter(file_list[1])
    #time_point = namer.time_pointer(file_list[1])
    print("Patient Number: %s Filter Number: %s" %(patientNumber, filterNumber))
    if mng.findPatient(patientNumber) == False:
        print('Previously unseen patient. Adding to database.')
        newPat = ptz.Patient(patNum=patientNumber)
        mng.addPatient(newPat)
        # This will create a new filter based on info scraped from filepath.
    # retrieve mongodb patient doc
    patientDoc = mng.retrieveDoc(patientNumber)
    newFilt = flz.Filter()
    try:
    #     # Attempt to get filter received date from record
        newFilt.DateRec = [patientDoc['filters'][item]['DateRec'] for item in patientDoc['filters'] if item == filterNumber][0]
        #print([patientDoc['filters'][item] for item in patientDoc['filters'] if item == filterNumber][0])
    except KeyError:
    #     # If no record ask for date.
         #newFilt.DateRec = str(cal.getDate('Select date sample was received.'))
         print("No date found!")
    # newFilt.DatePro = str(cal.getDate('Select date sample was processed.'))
    # newFilt.DateIm = str(cal.getDate('Select date sample was imaged.'))
    dict_images = {}
    for item in file_list:
        name = imz.Image().name_scrape(item)
        new_image = imz.Image()
        new_image.data_scrape(item)
        new_image = new_image.jsonable()
        dict_images[name] = new_image
    newFilt.images = dict_images
    newFilt.data_calc()
    for item in patientDoc['filters']:
        if item == filterNumber:
            print("Hit " + filterNumber)
            patientDoc['filters'][item] = newFilt.jsonable()
    #print(patientDoc)
    mng.shoveDoc(patientDoc)
    sys.exit()

if __name__ == '__main__':
    main()