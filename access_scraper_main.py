import pandas as pd
import numpy as np
from sample_adder import add_scrape
import datetime

def main():
    samples = pd.read_excel("C:\\Users\\Landon\\Desktop\\Database_Oct292014.xlsx")
    # Get list of patients
    patients = np.unique(samples['PatientID'])
    # Iterate through patients
    for patient in patients:
        frame = samples.loc[samples['PatientID'] == patient].sort_values("DateReceived")
        for index, row in frame.iterrows():
            #print(datetime.datetime.strftime(row['DateReceived'].to_pydatetime(), "%Y-%m-%d"))
            add_scrape(row['PatientID'], row['FilterID'], datetime.datetime.strftime(row['DateReceived'].to_pydatetime(), "%Y-%m-%d"))

if __name__ == "__main__":
    main()