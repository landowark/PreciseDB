import os
from DB_DIR import mongo as mng
import pandas as pd

master = pd.DataFrame()


for patient in mng.getPatientList():
    order = ["Patient ID", 'Gleason Score (+0m)', 'TNM Staging (+0m)', 'PSA 6 months after continued ADT', 'PSA 6 months after complete radiotherapy']
    new_dict = {}
    patient_dict = mng.retrieveDoc(patient)
    del patient_dict['filters']
    new_dict['Patient ID'] = patient_dict['_id']
    new_dict['Gleason Score (+0m)'] = str(patient_dict['procedures'][sorted(list(patient_dict['procedures'].keys()))[-1]]["Gleason"])
    new_dict['TNM Staging (+0m)'] = patient_dict['tScore']
    new_dict['PSA 6 months after continued ADT'] = patient_dict['sensitivity']['0.1']['psa6moafadt']
    new_dict['PSA 6 months after complete radiotherapy'] = patient_dict['sensitivity']['0.1']['psa6mafcompleterad']
    series = pd.Series(new_dict)
    master = master.append(series, ignore_index=True)

master = master[order]
master.index += 1 
master.to_excel("blah.xlsx")