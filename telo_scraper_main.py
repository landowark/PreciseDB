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
import namer
import mongo as mng
import lw_calendar as cal #custom calendar widget to choose dates
import sys
from PyQt5 import QtGui, QtWidgets #for calling QApplication in main (necessary to prevent multiple calls in fxns)

def main():
    app = QtWidgets.QApplication.instance()
    # checks if QApplication already exists
    if not app: # create QApplication if it doesnt exist 
        app = QtWidgets.QApplication(sys.argv)
    pathName = fg.get_dir()
    file_list = fg.recur_find(pathName, 'xlsx')
    patientNumber = namer.parsePatient(file_list[1])
    filterNumber = namer.parseFilter(file_list[1])
    time_point = namer.time_pointer(file_list[1])
    print("Patient Number: %s Filter Number: %s Time Point: %s" %(patientNumber, filterNumber, time_point))
    #retrieve mongodb patient doc    
    patientDoc = mng.retrieveDoc(patientNumber)
    if patientDoc == None:
        pass
        # This will create a new filter.
    newFilt = flz.Filter(filterNumber, time_point)
    newFilt.DateRec = patientDoc['Filter_' + filterNumber]['DateRec']
    newFilt.DatePro = str(cal.getDate('Select date sample was processed.'))
    newFilt.DateIm = str(cal.getDate('Select date sample was imaged.'))
    dict_images = {}
    for item in file_list:
        name = imz.Image().name_scrape(item)
        new_image = imz.Image()
        new_image.data_scrape(item)
        new_image = new_image.jsonable()
        dict_images[name] = new_image
    newFilt.images = dict_images
    newFilt.data_calc()
    patientDoc['Filter_' + filterNumber] = newFilt.jsonable()
    mng.shoveDoc(patientDoc)    

if __name__ == '__main__':
    main()
    sys.exit()