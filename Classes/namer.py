# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 10:30:33 2015
This module will be used to scrape patient, filter and 
timepoint info from the filepath selected by the user.
@author: Landon
"""
import os
import logging
import re
from DB_DIR.mongo import db_name

logger = logging.getLogger("mainUI.namer")

def parsePatient(input_string):
    print(db_name)
    if db_name == 'precise_actual':
        # compile regular expression to match
        patient_ex = re.compile(r'P0\d{3}|\d{3}?')
        # search input string for pattern
        patientNumber = patient_ex.search(input_string).group()
        if len(patientNumber) == 3:
            patientNumber = 'P0' + patientNumber
    elif db_name == 'quon_actual':
        patient_ex = re.compile(r'MB0\d{3}PR|\d{3}?')
        # search input string for pattern
        patientNumber = patient_ex.search(input_string).group()
        if len(patientNumber) == 3:
            patientNumber = 'MB0' + patientNumber + "PR"
    else:
        raise KeyError()
    return(patientNumber)

    
def parseFilter(input_string):
    filter_ex = re.compile(r'-\d{4}|1\dAA\d{4}')
    filterNumber = filter_ex.search(input_string).group()
    if len(filterNumber) == 5:
        filterNumber = '18AA' + filterNumber[1:]
    return(filterNumber)


def parseImage(file_path):
    # import re
    # imageNumRegex = re.compile(r'Image\d{4}')
    # imageName = imageNumRegex.search(file_path)
    # try:
    #     return(imageName.group())
    # except AttributeError as e:
    #     print(file_path, e)
    return os.path.splitext(os.path.basename(file_path))[0]
    
def time_pointer(file_path):
    tpRegex = re.compile(r'(\+\d?\dm)')
    timePoint = tpRegex.search(file_path)
    new = timePoint.group() 
    if len(new) <= 3:
        new = new[0] + '0' + new[1:]
    return(new)