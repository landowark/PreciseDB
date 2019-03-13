import datetime
import os

from sklearn.datasets import make_blobs
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import normalize as norm
from numpy.random import rand, randint
from numpy.core import ndarray
import pandas as pd
from DB_DIR import mongo as mng


# check to make certain data and data labels have same length
def check_length(data_array, label_array):
    assert len(data_array) == len(label_array)


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
    #print("Optimal number of clusters = {}".format(optimal_clusters))
    return optimal_clusters


def do_fitting(X: ndarray, optimal_clusters: int):
    km = KMeans(n_clusters=optimal_clusters, init='k-means++', n_init=10, max_iter=300, tol=1e-04, random_state=0)
    y_km = km.fit(X)
    check_length(X, y_km.labels_)
    return y_km, km


def make_chart(X: ndarray, y_km: KMeans, km: KMeans, optimal_clusters: int, x_label="", y_label=""):
    for jjj in range(0, optimal_clusters):
        plt.scatter(X[y_km.labels_ == jjj, 0], X[y_km.labels_ == jjj, 1], marker='o', s=50,
                    label="cluster {}".format(jjj + 1), edgecolors='black')
    plt.scatter(km.cluster_centers_[:, 0], km.cluster_centers_[:, 1], c='red', marker='*', s=250, label="centroid",
                edgecolors='black')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid()
    plt.show()


def make_summary(X_df_indices, cluster_labels):
    # todo make an excel sheet with a summary of which row index goes to which column
    pass


def perform_clustering(X_df: pd.DataFrame):
    X = X_df.to_numpy()
    X = norm(X, axis=0)
    optimal_clusters = get_optimal_number_clusters(X)
    y_km, km = do_fitting(X, optimal_clusters)
    X_label = X_df.columns.values[0]
    Y_label = X_df.columns.values[1]
    make_chart(X=X, y_km=y_km, km=km, optimal_clusters=optimal_clusters, x_label=X_label, y_label=Y_label)
    df = pd.DataFrame(data=y_km.labels_, index=X_df.index.values, columns=['Cluster #'])
    # print(df)
    tod = datetime.datetime.now().strftime("%A - %B %d, %Y")
    writer = pd.ExcelWriter(os.path.join(os.path.expanduser('~')), 'Desktop', 'kmeans-output-%s.xlsx' % tod)
    df.to_excel(writer, "kmeans")
    writer.save()


def construct_df_for_parameter(parameter:str):
    patient_list = mng.getPatientList()
    


if __name__ == "__main__":
    # Make toy data
    random_cluster_number = randint(2,6)
    #print("Number of starting clusters = {}".format(random_cluster_number))
    X, y = make_blobs(n_samples=150, n_features=2, centers=random_cluster_number, cluster_std=0.5, shuffle=True, random_state=0)
    #X = rand(500, 2)
    X_series = pd.DataFrame(X, columns=['Foo', 'Bar'])
    print(X_series)
    perform_clustering(X_series)