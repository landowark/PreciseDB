import pymongo as mng
from datetime import datetime

def nadir_scrape(patNum, psas):
    try:
        nadir_value = min([item[1] for item in psas])
        nad_idx = [item[1] for item in psas].index(nadir_value)
        nadir_date = psas[nad_idx][0]
        nadir_value = psas[nad_idx][1]
        print("%s reached a nadir of %s on %s \n" % (patNum, nadir_value, nadir_date))
        previous = 0
        for item in psas:
            if item[1] > nadir_value and item[1] > previous and item[0] > nadir_date:
                previous = item[1]
                print("... and reached a new high of %s on %s \n" % (item[1], item[0]))
    except ValueError as e:
        pass


if __name__ == "__main__":
    db = mng.MongoClient().prostate_actual
    patients = [doc for doc in db.patient.find()]
    filepath = ""
    for patient in patients:
        patNum = patient['_id']
        filterdates = [patient['filters'][thing]['DateRec'] for thing in patient['filters'].keys()]
        filterdates = [datetime.strptime(item, "%Y-%m-%d").timestamp() for item in filterdates]
        startdate = min(filterdates)
        raw_psas = []

        psaTimes = patient['PSAs'].keys()
        psaTimes = [datetime.strptime(item, "%Y-%m-%d").timestamp() for item in psaTimes]
        psaTimes = [datetime.fromtimestamp(item) for item in psaTimes]
        psaValues = patient['PSAs'].values()
        psas = sorted(list(zip(psaTimes, psaValues)))
        for element in psas:
            if element[0].timestamp() < startdate:
                psas.remove(element)
        nadir_scrape(patNum, psas)
