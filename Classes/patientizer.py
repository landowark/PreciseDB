# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 11:46:16 2015

This holds the class info for the patient data

@author: Landon
"""

class Patient(object):
    
    def __init__(self, patNum='0'):
        self._id = patNum
        self.tScore = ''
        self.DRE = ''
        self.PSAs = {}
        self.procedures = {}
        self.filters = {}
        self.treatments = {}
        self.institute = ''
        
    def jsonable(self):
        return self.__dict__
