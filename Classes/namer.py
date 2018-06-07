# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 10:30:33 2015
This module will be used to scrape patient, filter and 
timepoint info from the filepath selected by the user.
@author: Landon
"""
import logging

logger = logging.getLogger("mainUI.namer")

def parsePatient(input_string):
    import re
    # compile regular expression to match
    # print("Parsing input string %s" % input_string)
    patient_ex = re.compile(r'MB0\d{3}P?R?|\d{3}?')
    patientNumber = patient_ex.search(input_string).group()
    if len(patientNumber) == 3:
        patientNumber = 'MB0' + patientNumber + 'PR'
    elif len(patientNumber) == 6:
        patientNumber = patientNumber + 'PR'
    return(patientNumber)    
    
def parseFilter(input_string):
    import re
    filter_ex = re.compile(r'-\d{4}|1\dAA\d{4}')
    filterNumber = filter_ex.search(input_string).group()
    if len(filterNumber) == 5:
        filterNumber = '15AA' + filterNumber[1:]
    return(filterNumber)

def parseImage(file_path):
    import re
    imageNumRegex = re.compile(r'Image\d{4}')
    imageName = imageNumRegex.search(file_path)
    try:
        return(imageName.group())
    except AttributeError as e:
        print(file_path, e)
    
def time_pointer(file_path):
    import re
    tpRegex = re.compile(r'(\+\d?\dm)')
    timePoint = tpRegex.search(file_path)
    new = timePoint.group() 
    if len(new) <= 3:
        new = new[0] + '0' + new[1:]
    return(new)