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
        self.telomeres = {}
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
        inNucleus = sorted(inNucleus)
        #assert inNucleus[0] < inNucleus[1]
        #print(inNucleus)
        inNucleus = [inNucleus[1], inNucleus[3], inNucleus[5], inNucleus[7], inNucleus[9], inNucleus[10], inNucleus[11], inNucleus[13]]
        nucData = list(data['spots number'].iloc[inNucleus])

        spotnum = [int(iii) for iii in list(data['spots number'].iloc[inSignals].values)]
        isAgg = [int(iii) for iii in list(data['Aggregates'].iloc[inSignals].values)]
        teloDist = [float(iii) for iii in list(data['Distance from nucl. center [%]'].iloc[inSignals].values)]
        teloInt = [int(iii) for iii in list(data['Intensity'].iloc[inSignals].values)]
        teloX = [int(iii) for iii in list(data['x'].iloc[inSignals].values)]
        teloY = [int(iii) for iii in list(data['y'].iloc[inSignals].values)]
        teloZ = [int(iii) for iii in list(data['z'].iloc[inSignals].values)]
        teloX1 = [int(iii) for iii in list(data['x1'].iloc[inSignals].values)]
        teloY1 = [int(iii) for iii in list(data['y1'].iloc[inSignals].values)]
        teloZ1 = [int(iii) for iii in list(data['z1'].iloc[inSignals].values)]
        pretelomeres = list(zip(spotnum, teloInt, teloDist, isAgg, teloX, teloY, teloZ, teloX1, teloY1, teloZ1))

        for telo in pretelomeres:
            newtelo = {}
            newtelo['int'] = telo[1]
            newtelo['dist'] = telo[2]
            newtelo['agg'] = telo[3]
            newtelo['X'] = telo[4]
            newtelo['Y'] = telo[5]
            newtelo['Z'] = telo[6]
            newtelo['x1'] = telo[7]
            newtelo['y1'] = telo[8]
            newtelo['z1'] = telo[9]
            self.telomeres[str(telo[0]).zfill(3)] = newtelo
        #print(self.telomeres)
        self.meanDist = float(np.mean(data['Distance from nucl. center [%]'].iloc[inSignals].values))
        self.sigNum = len(self.telomeres)
        self.meanIntAll = nucData[0]
        self.meanIntNorm = nucData[1]
        self.prcAgg = nucData[2]
        self.ACRatio = nucData[3]
        self.nucX = nucData[4]
        self.nucY = nucData[5]
        self.nucZ = nucData[6]
        self.nucVol = nucData[7] * 0.002081 #presumably this is what Julius and Sabine hashed out -LW
        self.sigPerVol = self.sigNum/self.nucVol
        self.nucDia = float(6 * (self.nucVol / np.pi)) ** (1/3)
        #print(self.telomeres)
        return(self.jsonable())
    
    def name_scrape(self, file_path):
        import re   
        imageNumRegex = re.compile(r'Image\d{4}')
        imageName = imageNumRegex.search(file_path)
        return(imageName.group())
    
    def jsonable(self):
        return self.__dict__