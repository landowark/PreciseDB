'''
For pulling clinical info out of excel files sent from Jean
'''

import pandas as pd
from Classes import namer
from MongoInterface import mongo as mng
import datetime
import logging

logger = logging.getLogger("mainUI.ClinicalScraper")

def main(filepath_clinical = "C:\\Users\\Landon\\Dropbox\\Documents\\Student Work\\Data\\Clinical Data\\CTC_RT_14Feb17 updating APRIL 2018 for Landon.xlsx"):#, filepath_PSA="C:\\Users\\Landon\\Dropbox\\Documents\\Student Work\\Data\\Clinical Data\\psa_aug182017.xls"):
    # read into dataframes
    df_clinical = pd.read_excel(filepath_clinical, sheet_name="Clinical Data")
    #df_PSA = pd.read_excel(filepath_PSA)
    # Get indexes of patient numbers
    patidx_clinical = list(set(df_clinical.index[df_clinical['MB'].notnull()]))
    # Not sure why the below line is there.
    patidx_clinical.append(df_clinical.index[-1])
    patidx_clinical.sort()
    # Get patients from indices
    patients = list(df_clinical['MB'].iloc[patidx_clinical[:-1]])
    # iterate through each patient
    for iii, patientNumber in enumerate(patients):
        logger.info("Running clinical scrape of %s" % patientNumber)
        patientNumber = namer.parsePatient(patientNumber)
        # slice df_clinical, remembering to make new df_clinical start at 0.
        new_df_clinical = df_clinical.iloc[patidx_clinical[iii]:patidx_clinical[iii + 1] - 1].reset_index()
        # Get PSAs
        PSAidx = list(set(new_df_clinical.index[new_df_clinical['PSA'].notnull()]))
        PSA = {}
        for item in PSAidx:
            # scrape PSA date
            PSADate = new_df_clinical['Date'].iloc[item].date()
            PSADate = datetime.date.strftime(PSADate, '%Y-%m-%d')
            # scrape PSA level
            PSALevel = float(new_df_clinical['PSA'].iloc[item])
            PSA[PSADate] = PSALevel
        # Get procedures
        procidx = list(set(new_df_clinical.index[new_df_clinical['Procedure'].notnull()]))
        procedures = {}
        for item in procidx:
            # scrape procedure date
            procDate = new_df_clinical['Procedure date'].iloc[item].date()
            procDate = datetime.date.strftime(procDate, '%Y-%m-%d')
            # scrape procedure
            proc = new_df_clinical['Procedure'].iloc[item]
            # scrape Gleason Score
            Gleason = new_df_clinical['Gleason Score'].iloc[item]
            PriSec = str(new_df_clinical['Primary/Secondary'].iloc[item]).replace('.0', '')
            # scrape number of cores
            try:
                numcores = int(new_df_clinical['Number of Cores'].iloc[item])
            except ValueError:
                numcores = str(new_df_clinical['Number of Cores'].iloc[item])
            try:
                poscores = int(new_df_clinical['Number of Cores Pos'].iloc[item])
            except:
                poscores = str(new_df_clinical['Number of Cores Pos'].iloc[item])
            procedures[procDate] = {'Procedure':proc, '#Cores':numcores, '#Positive Cores':poscores, 'Primary/Secondary': PriSec, 'Gleason':Gleason}
        # Get treatments
        trxidx = list(set(new_df_clinical.index[new_df_clinical['Treatment'].notnull()]))
        treatments = {}
        for item in trxidx:
            # try converting treatment dates to python datetime object, if fails make string
            try:
                trxDate = new_df_clinical['Treatment date'].iloc[item].date()
                trxDate = datetime.date.strftime(trxDate, '%Y-%m-%d')
            except AttributeError:
                trxDate = new_df_clinical['Treatment date'].iloc[item]
            except ValueError:
                print("Error using %s as treatment date. Skipping." % trxDate)
                continue
            trx = new_df_clinical['Treatment'].iloc[item]
            try:
                endDate = new_df_clinical['Last Give/End Date'].iloc[item].date()
                endDate = datetime.date.strftime(endDate, '%Y-%m-%d')
            except ValueError:
                endDate = "N/A"
            except AttributeError:
                endDate = "N/A"
            treatments[trxDate] = {'Treatment':trx, 'End Date':endDate}
        DRE = df_clinical['DRE'].iloc[patidx_clinical[iii]]
        tScore = df_clinical['Stage'].iloc[patidx_clinical[iii]]
        status = df_clinical['Status'].iloc[patidx_clinical[iii]]
        # retrieve and update patient doc from Mongo
        print("Updating MongoDB.")
        patientDoc = mng.retrieveDoc(patientNumber)
        patientDoc['status'] = status
        patientDoc['tScore'] = tScore
        patientDoc['DRE'] = DRE
        patientDoc['procedures'] = procedures
        patientDoc['PSAs'] = PSA
        patientDoc['treatments'] = treatments
        mng.shoveDoc(patientDoc)



if __name__ == '__main__':
    main()