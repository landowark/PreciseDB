'''
For pulling sample info out of excel file exported from my Access Database.
'''


import pandas as pd
import numpy as np
from .sample_adder import add
import datetime
import logging

logger = logging.getLogger("mainUI.table_scraper")

def main():
    samples = pd.read_excel("C:\\Users\\Landon\\Desktop\\Database_Oct292014.xlsx")
    # Get list of patients
    patients = np.unique(samples['PatientID'])
    # Iterate through patients
    for patient in patients:
        # get cells where PatientID == patient number, sort by date
        frame = samples.loc[samples['PatientID'] == patient].sort_values("DateReceived")
        for index, row in frame.iterrows():
            #print(datetime.datetime.strftime(row['DateReceived'].to_pydatetime(), "%Y-%m-%d"))
            add(['PatientID'], row['FilterID'], datetime.datetime.strftime(row['DateReceived'].to_pydatetime(), "%Y-%m-%d"))

if __name__ == "__main__":
    main()