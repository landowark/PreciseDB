# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:33:31 2015
This module will take the input from a teloview xl file and convert it to a
new image in the patient json structure.
@author: Landon
"""
class Image():
    
    def __init__(self):
        self.sigNum = 0
        self.meanIntAll = 0
        self.meanDist = 0
        self.meanIntNorm = 0
        self.ACRatio = 0
        self.prcAgg = 0
        self.nucX = 0
        self.nucY = 0
        self.nucZ = 0
        self.nucVol = 0
        self.teloInt = []
        self.teloDist = []
        self.isAgg = []
        self.sigPerVol = 0
        self.nucDia = 0
        
    def data_scrape(self, file_path):
        import pandas as pd
        import numpy as np
        data = pd.read_excel(file_path)
        inSignals = data.index[data['x'].notnull()]
        inNucleus = set(data.index[data['spots number'].notnull()]).difference(inSignals)
        inSignals = list(inSignals)
        inNucleus = list(inNucleus)
        inNucleus = [inNucleus[1], inNucleus[3], inNucleus[5], inNucleus[7], inNucleus[9], inNucleus[10], inNucleus[11], inNucleus[13]]
        nucData = list(data['spots number'].iloc[inNucleus])
        self.isAgg = [int(iii) for iii in list(data['Aggregates'].iloc[inSignals].values)]
        self.teloDist = [float(iii) for iii in list(data['Distance from nucl. center [%]'].iloc[inSignals].values)]
        self.teloInt = [int(iii) for iii in list(data['Intensity'].iloc[inSignals].values)]
        self.meanDist = float(np.mean(data['Distance from nucl. center [%]'].iloc[inSignals].values))
        self.sigNum = len(self.teloInt)
        self.meanIntAll = nucData[0]
        self.meanIntNorm = nucData[1]
        self.prcAgg = nucData[2]
        self.ACRatio = nucData[3]
        self.nucX = nucData[4]
        self.nucY = nucData[5]
        self.nucZ = nucData[6]
        self.nucVol = nucData[7] * 0.002081
        self.sigPerVol = self.sigNum/self.nucVol
        self.nucDia = float(6 * (self.nucVol / np.pi)) ** (1/3)
        return(self.jsonable())
    
    def name_scrape(self, file_path):
        import re   
        imageNumRegex = re.compile(r'Image\d{4}')
        imageName = imageNumRegex.search(file_path)
        return(imageName.group())
    
    def jsonable(self):
        return self.__dict__