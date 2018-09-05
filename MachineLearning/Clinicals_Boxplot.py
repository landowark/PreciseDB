
from MachineLearning.Preprocessing import DRE_Closest_Result as dre
from MachineLearning.Preprocessing import TimePointer, Procedures_Grabber, PCA
from MachineLearning.Preprocessing import tScore_Scraper as tss
from MongoInterface import mongo as mng
from matplotlib import pyplot as plt
from difflib import get_close_matches
import pandas as pd

def Get_Clinicals(clinical_para="DRE", telo_para="maxInt", tpoint="+00m"):
    df = pd.DataFrame(index=None)
    telos = mng.get_timepoint_for_all(tpoint)
    df[tpoint] = [patient for patient in telos]
    # Because gleason, #cores occurs within the 'procedures' extra steps are needed.
    if clinical_para.lower() == "gleason" or clinical_para.lower() == "primary/secondary" or clinical_para.lower() == 'cores':
        procedures = [mng.retrieveDoc(patientnum)['procedures'] for patientnum in df[tpoint]]
        df[clinical_para] = [Procedures_Grabber(procedure, clinical_para) for procedure in procedures]
    else:
        # get basic clinicals
        df[clinical_para] = [str(mng.retrieveDoc(patientnum)[clinical_para]).replace('nan', 'Unknown').capitalize() for patientnum in df[tpoint]]
    # preprocessing steps
    if clinical_para.lower() == "dre":
        # perform DRE preprocessing (collapsing strings)
        df[clinical_para] = [dre(clinical)[0] for clinical in df[clinical_para]]
    elif clinical_para.lower() == "tscore":
        df[clinical_para] = [tss(clinical) for clinical in df[clinical_para]]
    if telo_para.lower() == "pca":
        df[telo_para] = PCA(telos)
    else:
        df[telo_para] = [telos[blah][telo_para] for blah in telos.keys()]
    df = df[[tpoint, clinical_para, telo_para]]
    return df

def Group_By_Clinical(data):
    group = {}
    # quick removal of data that contains nans
    clinicals = sorted(set(data.iloc[:, 1]))
    for item in clinicals:
        df = data[data.iloc[:,1] == item]
        df = df[df.iloc[:,2] >= 1.0]
        group[item] = list(df.iloc[:,2])
    return group

def box_whisker(data, parameters):
    data_to_plot = list(data.values())
    counts = [str(len(instance)) for instance in data_to_plot]
    new = list(data.keys())
    labs = [str(name) + "\n(n=" + str(count) + ")" for name, count in zip(new, counts)]
    plt.boxplot(data_to_plot, labels=labs)
    plt.ylabel(parameters['teloview_parameter'])
    plt.title(parameters['clinical_parameter'] + " " + parameters['timepoint'])
    plt.show()

if __name__ == '__main__':

    clin_p = input("Input clinical parameter: ")  or "Gleason"
    telo_p = input("Input teloview parameter: ") or "numSig"
    tpoint = input("Input timepoint parameter: ")  or "+00m"

    possible_clins = get_close_matches(clin_p, ['DRE', 'tScore', 'Cores', "Gleason", "Primary/Secondary"])
    possible_telos = get_close_matches(telo_p,['ACRatio', 'maxInt', 'meanInt', 'nucDia', 'nucVol', 'numSig', 'p1qrt', 'p2qrt', 'p3qrt', 'p4qrt', 'peakNumSig', 'prAgg', 'prDist', 'sigPerVol', 'pca'])
    data = Get_Clinicals(possible_clins[0], possible_telos[0], tpoint)
    groups = Group_By_Clinical(data)
    parameters = {'clinical_parameter':clin_p, 'teloview_parameter':telo_p, 'timepoint':tpoint}
    box_whisker(groups, parameters)