import pandas as pd
import numpy as np
from datetime import datetime
from Scripts.find_nadir import nadir_scrape

filepath = ""
df = pd.read_excel(filepath)
patients = df['MBTB#']
np.unique(patients)
thing = list(np.unique(patients))
for patient in thing:
    patNum = patient
    indices = df.index[df['MBTB#'] == patient].tolist()
    psa_dates = [datetime.strptime(str(item), "%Y-%m-%d %H:%M:%S") for item in df['date_test_pt_test'].iloc[indices]]
    #print(patNum, psa_dates)
    psa_values = df['test_value'].iloc[indices]
    psas = sorted(list(zip(psa_dates, psa_values)))
    #print(patNum, psas)
    nadir_scrape(patNum, psas)
