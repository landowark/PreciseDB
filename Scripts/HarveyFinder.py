from MongoInterface import mongo as mng
from ScrapeTeloView import chart_maker as cm
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
    df1 = pd.DataFrame(columns=["Patient", treatment + " " + trx_time, "+6m Closest PSA", "Diff (days)", "PSA Level"])
    patients = mng.getPatientList()
    for patient in patients:
        try:
            trx_relevant = mdates.num2date([date[trx_time] for date in cm.getTreatments(patient) if treatment in date['name']][0]).date()
        except IndexError as e:
            print(e)
            continue
        six_months = (trx_relevant + relativedelta(months=+6))
        psas = mng.retrieveDoc(patient)['PSAs']
        psa_dates = [dt.datetime.strptime(date, "%Y-%m-%d").date() for date in list(psas.keys())]
        closest = nearest(psa_dates, six_months)
        diff = closest - six_months
        psa_level = psas[closest.strftime("%Y-%m-%d")]
        df1 = df1.append({'Patient': patient, treatment + " " + trx_time: trx_relevant, "+6m Closest PSA": closest, "Diff (days)": diff, "PSA Level": psa_level}, ignore_index=True)
    return df1

def main():
    df1 = treatment_getter("Bicalutamide")
    df2 = treatment_getter("RT")
    writer = pd.ExcelWriter('C:\\Users\\Landon\\Desktop\\Quon Prostate Friday - June 15, 2018\\HarveyFinder-output.xlsx')
    df1.to_excel(writer, "Bicalutamide")
    df2.to_excel(writer, "RT")
    writer.save()

if __name__ == "__main__":
    main()