import os

import DB_DIR.mongo
from DB_DIR import mongo as mng
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.dates as mdates

def nearest(psa_dates, six_months):
    return min(psa_dates, key=lambda x: np.absolute(x - six_months))

def treatment_getter(treatment: str):
    if treatment == "RT":
        trx_time = "end"
    else:
        trx_time = "start"
    df1 = pd.DataFrame(columns=["Patient", treatment + " " + trx_time, "Closest PSA to +6m", "Diff (days)", "PSA Level"])
    patients = mng.getPatientList()
    for patient in patients:
        try:
            trx_relevant = mdates.num2date([date[trx_time] for date in DB_DIR.mongo.getTreatments(patient) if treatment in date['name']][0]).date()
        except IndexError as e:
            print(e)
            continue
        six_months = (trx_relevant + relativedelta(months=+6))
        psas = mng.retrieveDoc(patient)['PSAs']
        psa_dates = [dt.datetime.strptime(date, "%Y-%m-%d").date() for date in list(psas.keys())]
        closest = nearest(psa_dates, six_months)
        diff = closest - six_months
        psa_level = psas[closest.strftime("%Y-%m-%d")]
        app_dict = {'Patient': patient, treatment + " " + trx_time: trx_relevant, "Closest PSA to +6m": closest, "Diff (days)": diff, "PSA Level": psa_level}
        join_dict = parameter_getter(patient, closest)
        z = dict(list(app_dict.items()) + list(join_dict.items()))
        df1 = df1.append(z, ignore_index=True)
    return df1

def parameter_getter(patient: str, psa_closest):
    # Get closest sample to six months
    dicto = {}
    this_patient = mng.retrieveDoc(patient)['filters']
    zeroMon = this_patient[[filter for filter in this_patient.keys() if this_patient[filter]['tPoint'] == "+00m"][0]]
    dates = [dt.datetime.strptime(this_patient[item]['DateRec'], "%Y-%m-%d").date() for item in this_patient.keys()]
    samp_closest = nearest(dates, psa_closest).strftime("%Y-%m-%d")
    relevant = this_patient[[filter for filter in this_patient.keys() if this_patient[filter]['DateRec'] == samp_closest][0]]
    dicto['Closest Sample Date to psa Date'] = samp_closest
    for item in relevant.keys():
        if item != "CTCNum":
            try:
                dicto["Diff from +00m " + item] = relevant[item] - zeroMon[item]
            except TypeError:
                continue
    return dicto

def main():
    df1 = treatment_getter("Bicalutamide")
    print(df1)
    df2 = treatment_getter("RT")
    tod = dt.datetime.now().strftime("%A - %B %d, %Y")
    writer = pd.ExcelWriter(os.path.join(os.path.expanduser('~')), 'Desktop','HarveyFinder-output-%s.xlsx' % tod)
    df1.to_excel(writer, "Bicalutamide")
    df2.to_excel(writer, "RT")
    writer.save()

if __name__ == "__main__":
    main()