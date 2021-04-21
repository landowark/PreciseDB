import pymongo as pmg
import os
import pandas as pd
import itertools
import math
import numpy as np
from Scripts import sloper


used_tps = ["+00m", "+02m", "+06m"]


def get_all_filter_intensities(filter_dict: dict) -> list:
    # I like uncomprehensible list comprehensions!
    intensities = []
    images = list(filter_dict['images'].keys())
    for image in images:
        filter = filter_dict['images'][image]
        telomeres = list(filter['telomeres'].keys())
        for telomere in telomeres:
            intensities.append(filter_dict['images'][image]['telomeres'][telomere]['int'])
    return intensities


def get_all_patient_intensities(patient_dict: dict):
    pat = patient_dict['_id']
    filters = list(patient_dict['filters'].keys())
    intensities = {patient_dict['filters'][filter]['tPoint']:get_all_filter_intensities(patient_dict['filters'][filter]) for filter in filters if patient_dict['filters'][filter]['tPoint'] in used_tps}
    intensities = {item[0]: item[1] for item in sorted(intensities.items())}
    print(intensities)
    maximum = math.ceil(max(list(itertools.chain(*[value for value in intensities.values()]))) / 1000) * 1000
    bins = np.arange(0, maximum+1000, 1000)
    return {pat:{"timepoints":intensities, "bins":bins}}


def perform_filter_binning(intensities: list, bins: np.ndarray, name: str) -> pd.Series:
    data, index = np.histogram(intensities, bins=bins)
    try:
        series = pd.Series(data, index)
    except ValueError:
        data = np.append(data, [0])
        series = pd.Series(data, index)
    series.rename(name)
    return series


def make_patient_dataframe(patient_dict: dict) -> pd.DataFrame:
    bins = patient_dict['bins']
    series = {filter:perform_filter_binning(patient_dict['timepoints'][filter], bins, filter) for filter in patient_dict['timepoints']}
    df = pd.DataFrame(series)
    return df


def main():
    used_db = "quon_actual"

    db = pmg.MongoClient().get_database(used_db).patient
    patient_list = [doc['_id'] for doc in db.find().batch_size(10)]
    master = {}
    for patient in patient_list:
        try:
            doc = db.find_one({'_id': patient})
            timepoints = [doc['filters'][filter]['tPoint'] for filter in doc['filters']]
            if not all(elem in timepoints for elem in used_tps):
                continue
            # if len(doc['filters'].keys()) != 6:
            #     continue
            master.update(get_all_patient_intensities(doc))
        except IndexError:
            continue
        except ValueError:
            continue
    deleter = []
    # remove any patient with incomplete values
    for item in master:
        for tp in master[item]['timepoints'].keys():
            if master[item]['timepoints'][tp] == []:
                deleter.append(item)
            try:
                print(item, tp, max(master[item]['timepoints'][tp]))
            except ValueError:
                deleter.append(item)
    for item in deleter:
        try:
            del master[item]
        except KeyError:
            continue
    big_dict = {item:make_patient_dataframe(master[item]) for item in master}
    writer1 = pd.ExcelWriter(os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "master.xlsx"))
    writer2 = pd.ExcelWriter(os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "slopes.xlsx"))
    slope_dict = {}
    for item in big_dict:
        big_dict[item].to_excel(writer1, sheet_name=item, engine='xlsxwriter')
        this = sloper.main(big_dict[item], item)
        slope_dict[item] = {this[0][0][0]:float(this[0][0][1]), this[0][1][0]:float(this[0][1][1])}
    writer1.close()
    df2 = pd.DataFrame(slope_dict).transpose()
    df2.to_excel(writer2, sheet_name="master", engine='xlsxwriter')
    writer2.close()



if __name__ == "__main__":
    main()