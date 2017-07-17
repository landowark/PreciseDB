# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 12:58:54 2015
This module will contain all of the code necessary to put together the
filter objects.
@author: Landon
"""

import datetime

class Filter():
    
    def __init__(self, tPoint='+00m'):
        
        format = '%Y-%m-%d'
        self.tPoint = tPoint
        self.images = {}
        self.CTCNum = 0
        self.meanInt = 0
        self.prDist = 0
        self.prAgg = 0
        self.ACRatio = 0
        self.nucVol = 0
        self.nucDia = 0
        self.numSig = 0
        self.peakNumSig = 0
        self.p1qrt = 0
        self.p2qrt = 0
        self.p3qrt = 0
        self.p4qrt = 0
        self.sigPerVol = 0
        self.maxInt = 0
        self.PSA = 0
        self.DateRec = str(datetime.date(2014,1,1).strftime(format))
        #self.DatePro = str(datetime.date(2014,1,1).strftime(format))
        #self.DateIm = str(datetime.date(2014,1,1).strftime(format))
        
    def data_calc(self):
        import numpy as np
        '''Create and append data to lists'''
        sig_list = []        
        meanInt_list = []
        dist_list = []
        agg_list = []
        AC_list = []
        Vol_list = []
        int_list = []
        sigPerVol_list = []
        dia_list = []
        for item in self.images:
            sig_list.append(self.images[item]['sigNum'])
            meanInt_list.append(self.images[item]['meanIntAll'])
            dist_list.append(self.images[item]['meanDist'])
            agg_list.append(self.images[item]['prcAgg'])
            AC_list.append(self.images[item]['ACRatio'])            
            Vol_list.append(self.images[item]['nucVol'])
            sigPerVol_list.append(self.images[item]['sigPerVol'])
            dia_list.append(self.images[item]['nucDia'])
            for thing in self.images[item]['telomeres']:
                #print(self.images[item]['telomeres'][thing])
                int_list.append(self.images[item]['telomeres'][thing]['int'])
        '''Calculate values based on lists'''
        self.numSig = float(np.mean(sig_list))
        self.peakNumSig = int(np.max(sig_list))
        self.meanInt = float(np.mean(meanInt_list))
        self.prDist = float(np.mean(dist_list))
        self.prAgg = float(np.mean(agg_list))
        self.ACRatio = float(np.mean(AC_list))
        self.nucVol = float(np.mean(Vol_list))
        self.sigPerVol = float(np.mean(sigPerVol_list))
        self.nucDia = float(np.mean(dia_list))
        self.maxInt = int(np.max(int_list))
        self.quartiles(int_list)        
        
        #return(self.jsonable())
        
    def quartiles(self, int_list):
        import numpy as np
        dest = np.histogram(int_list, 4)
        quart_list = []
        for item in np.ravel(dest)[0]:
            quart_list.append(float((item / len(int_list)) * 100))
        self.p1qrt = quart_list[0]
        self.p2qrt = quart_list[1]
        self.p3qrt = quart_list[2]
        self.p4qrt = quart_list[3]
        
#    def fitDict(self, inputdict):
#        # fits incoming dictionary variables into this filter
#        for item in vars(self):
#            print(item + ':', inputdict[item])
        
        
    def jsonable(self):
        return self.__dict__