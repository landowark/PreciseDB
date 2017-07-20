'''
For pulling clinical info out of excel files sent from Jean
'''

import pandas as pd
import namer
import mongo as mng
import datetime

def main():
    filepath = "C:\\Users\\Landon\\Documents\\Student Work\\Data\\CTC_RT_14Feb17_Completed.xlsx"
    df = pd.read_excel(filepath, sheetname="Clinical Data")
    # Get indexes of patient numbers
    patidx = list(set(df.index[df['MB'].notnull()]))
    patidx.append(df.index[-1])
    patidx.sort()
    # Get patients from indices
    patients = list(df['MB'].iloc[patidx[:-1]])
    # iterate through each patient
    for iii, patientNumber in enumerate(patients):
        print(patientNumber)
        patientNumber = namer.parsePatient(patientNumber)
        # slice df, remembering to make new df start at 0.
        new_df = df.iloc[patidx[iii]:patidx[iii + 1] - 1].reset_index()
        #new_df = new_df.reset_index()
        #print(new_df)
        PSAs = list(new_df['PSA'])
        Dates = list(new_df['Date'])
        tots = zip(Dates, PSAs)
        DRE = df['DRE'].iloc[patidx[iii]]
        tScore = df['Stage'].iloc[patidx[iii]]
        # Get PSA
        PSA = {}
        for item in tots:
            PSA[str(item[0].date())] = float(item[1])
        # Get procedures
        procidx = list(set(new_df.index[new_df['Procedure'].notnull()]))
        procedures = {}
        for item in procidx:
            procDate = new_df['Procedure date'].iloc[item].date()
            procDate = datetime.date.strftime(procDate, '%Y-%m-%d')
            proc = new_df['Procedure'].iloc[item]
            Gleason = new_df['Gleason Score'].iloc[item]
            PriSec = str(new_df['Primary/Secondary'].iloc[item]).replace('.0', '')
            numcores = int(new_df['Number of Cores'].iloc[item])
            try:
                poscores = int(new_df['Number of Cores Pos'].iloc[item])
            except:
                poscores = str(new_df['Number of Cores Pos'].iloc[item])
            procedures[procDate] = {'Procedure':proc, '#Cores':numcores, '#Positive Cores':poscores, 'Primary/Secondary': PriSec, 'Gleason':Gleason}
        # Get treatments
        trxidx = list(set(new_df.index[new_df['Treatment'].notnull()]))
        treatments = {}
        for item in trxidx:
            try:
                trxDate = new_df['Treatment date'].iloc[item].date()
                trxDate = datetime.date.strftime(trxDate, '%Y-%m-%d')
            except AttributeError:
                trxDate = new_df['Treatment date'].iloc[item]
            trx = new_df['Treatment'].iloc[item]
            try:
                endDate = new_df['Last Give/End Date'].iloc[item].date()
                endDate = datetime.date.strftime(endDate, '%Y-%m-%d')
            except ValueError:
                endDate = "N/A"
            treatments[trxDate] = {'Treatment':trx, 'End Date':endDate}
        patientDoc = mng.retrieveDoc(patientNumber)
        patientDoc['tScore'] = tScore
        patientDoc['DRE'] = DRE
        patientDoc['procedures'] = procedures
        patientDoc['PSAs'] = PSA
        patientDoc['treatments'] = treatments
        mng.shoveDoc(patientDoc)

if __name__ == '__main__':
    main()
