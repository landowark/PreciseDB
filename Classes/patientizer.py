# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:46:16 2015

This holds the class info for the patient data

@author: Landon
"""
import datetime


class Patient(object):
    
    def __init__(self, patNum='0'):
        format = '%Y-%m-%d'
        self._id = patNum
        self.patient_num = 0
        self.tScore = ''
        self.DRE = ''
        self.PSAs = {}
        self.procedures = {}
        self.filters = {}
        self.treatments = {}
        self.initials = ''
        self.institute = ''
        self.DateRec = str(datetime.date(2014, 1, 1).strftime(format))
        self.mLBlood = 0
        self.receiver = ""
        
    def jsonable(self):
        return self.__dict__
