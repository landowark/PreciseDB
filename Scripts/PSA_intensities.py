import pymongo as pmg
import os
import pandas as pd
import itertools
import math
import numpy as np


analysis_type = "Exclusion" # "Sensitivity"
cutoff = ".1" # .5
PSA_file = os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project/Mary's Analyses", analysis_type + ".xlsx")
adtrad = "psa6mafcompleterad" # "psa6moafadt"

def get_intensity_quartiles(filtDict: dict) -> dict:
    return {"q1": float(filtDict['p1qrt']), "q2": float(filtDict['p2qrt']),
            "q3": float(filtDict['p3qrt']), "q4": float(filtDict['p4qrt'])}


def main():
    used_db = "quon_actual"
    df = pd.read_excel(PSA_file, sheet_name=cutoff + " cutoff")
    db = pmg.MongoClient().get_database(used_db).patient
    patient_list = [doc['_id'] for doc in db.find().batch_size(10)]
    master = {}
    for patient in patient_list:
        pd_patient = int(patient[3:-2])
        try:
            doc = db.find_one({'_id': patient})
            for filter in list(doc['filters'].keys()):
                if doc['filters'][filter]['tPoint'] == "+00m":
                    filtDict = doc['filters'][filter]
            master[patient] = get_intensity_quartiles(filtDict)
            index = df.loc[df['pt_id']==pd_patient].index[0]
            master[patient]["threshold"] = df.loc[index].at[adtrad]
        except IndexError:
            continue
    for patient in patient_list:
        check_condition = master[patient]['q1'] == 0.0 and master[patient]['q2'] == 0.0 and master[patient]['q3'] == 0.0 and master[patient]['q4'] == 0.0
        #print(patient, master[patient])
        if check_condition or "threshold" not in list(master[patient].keys()):
            del master[patient]
    #print(master['MB0431PR'])
    writer2 = pd.ExcelWriter(os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "quartiles.xlsx"))
    df2 = pd.DataFrame(master).transpose()
    df2.to_excel(writer2, sheet_name="master", engine='xlsxwriter')
    writer2.close()



if __name__ == "__main__":
    main()