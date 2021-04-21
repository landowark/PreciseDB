import datetime
import os
from io import BytesIO
from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize as norm
from numpy.random import rand, randint
from numpy.core import ndarray
import numpy as np
import pandas as pd
import pymongo as mng


# check to make certain data and data labels have same length
def check_length(data_array, label_array):
    assert len(data_array) == len(label_array)


def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]


def get_optimal_number_clusters(X: ndarray) -> int:
    # Silhouette method for finding optimal cluster number (computational)
    silhouettes = {}
    for iii in range(2, len(X)):
        km = KMeans(n_clusters=iii, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0)
        new_km = km.fit(X)
        label = new_km.labels_
        silhouettes[iii] = silhouette_score(X, label, metric='euclidean')
    reverse_sil = dict(zip(silhouettes.values(), silhouettes.keys()))
    optimal_clusters = reverse_sil[max(silhouettes.values())]
    # print("Optimal number of clusters = {}".format(optimal_clusters))
    return optimal_clusters


def do_fitting(X: ndarray, optimal_clusters: int):
    km = KMeans(n_clusters=optimal_clusters, init='k-means++', n_init=10, max_iter=300, tol=1e-04, random_state=0)
    y_km = km.fit(X)
    check_length(X, y_km.labels_)
    return y_km, km


def make_chart(X: ndarray, y_km: KMeans, km: KMeans, optimal_clusters: int, x_label="", y_label=""):
    #fig, axes = plt.subplots(figsize=(15,15))
    for jjj in range(0, optimal_clusters):
        plt.scatter(X[y_km.labels_ == jjj, 0], X[y_km.labels_ == jjj, 1], marker='o', s=50,
                    label="cluster {}".format(jjj + 1), edgecolors='black')
    plt.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1], c='red', marker='*', s=250, label="centroid",
                edgecolors='black')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid()
    plt.rcParams["figure.figsize"] = [10,10]
    # plt.show()

    imgdata = BytesIO()
    plt.savefig(imgdata, format="png")
    plt.clf()
    imgdata.seek(0)
    return imgdata


def make_summary(X_df_indices, cluster_labels):
    # todo make an excel sheet with a summary of which row index goes to which column
    pass


def perform_clustering(X_df: pd.DataFrame, parameter: str):
    timepoints = ["+00m", "+02m", "+06m", "+12m", "+18m", "+24m"]
    writer = pd.ExcelWriter(os.path.join(os.path.expanduser('~'), 'Desktop', 'kmeans-output-%s.xlsx' % parameter))
    workbook1 = writer.book
    parameter_df = pd.DataFrame(index=X_df.index)
    for iii, timepoint in enumerate(timepoints):
        try:
            series_str = "{0} vs. {1}".format(timepoints[iii], timepoints[iii+1])
            df2 = X_df.iloc[:, [iii,iii+1]]
            X = df2.values
            X = norm(X, axis=0)
            optimal_clusters = get_optimal_number_clusters(X)
            y_km, km = do_fitting(X, optimal_clusters)
            X_label = X_df.columns.values[0]
            Y_label = X_df.columns.values[1]
            img = make_chart(X=X, y_km=y_km, km=km, optimal_clusters=optimal_clusters, x_label=X_label, y_label=Y_label)
            this_series = pd.Series(data=y_km.labels_, index=X_df.index.values)#, columns=["{0} vs. {1}".format(timepoints[iii], timepoints[iii+1])])
            parameter_df[series_str] = this_series
            worksheet = workbook1.add_worksheet(series_str)
            worksheet.insert_image(0, 5, "", {'image_data': img})
        except IndexError as e:
            continue
    #print(parameter_df)
    parameter_df.to_excel(writer, "kmeans-" + parameter)
    writer.save()


def getPatientList():
    # Get list of all patients in mongoDB
    db = mng.MongoClient().quon_actual
    return [doc['_id'] for doc in db.patient.find().batch_size(10)]


def get_filter_by_tPoint(patientNumber, tPoint):
    # Get filter by timepoint
    db = mng.MongoClient().quon_actual.patient
    doc = db.find_one({'_id': patientNumber})
    filtDict = {}
    for filter in list(doc['filters'].keys()):
        if doc['filters'][filter]['tPoint'] == tPoint:
            filtDict = doc['filters'][filter]
    try:
        del filtDict['images']
    except KeyError:
        return None
    return(filtDict)


def get_all_parameters():
    db = mng.MongoClient().quon_actual.patient
    para = []
    for patient in [db.find_one({'_id': patient}) for patient in getPatientList()]:
        try:
            measures = [patient['filters'][filter].keys() for filter in patient['filters'].keys()]
            for item in measures:
                for thing in list(item):
                    if thing not in para and thing not in ['images', 'tPoint', 'DateRec', 'CTCNum']:
                        para.append(thing)
        except KeyError:
            continue
    return para


def construct_df_for_parameter(parameter: str):
    patient_list = getPatientList()
    patient_dict = {}
    for patient in patient_list:
        try:
            month00 = get_filter_by_tPoint(patient, "+00m")[parameter]
            month02 = get_filter_by_tPoint(patient, "+02m")[parameter]
            month06 = get_filter_by_tPoint(patient, "+06m")[parameter]
            month12 = get_filter_by_tPoint(patient, "+12m")[parameter]
            month18 = get_filter_by_tPoint(patient, "+18m")[parameter]
            month24 = get_filter_by_tPoint(patient, "+24m")[parameter]
        except KeyError:
            continue
        except TypeError:
            continue
        patient_dict[patient] = {"+00m":month00, "+02m":month02, "+06m":month06, "+12m":month12, "+18m":month18, "+24m":month24}
    df = pd.DataFrame.from_dict(patient_dict, orient="index")
    df2 = df[(df.T != 0).all(axis=0)]
    perform_clustering(df2, parameter)
    #print(df2)


if __name__ == "__main__":
    for para in get_all_parameters():
        print(para)
        construct_df_for_parameter(para)