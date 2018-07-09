
from MachineLearning.Preprocessing import DRE_Closest_Result as dre
from MachineLearning.Preprocessing import TimePointer, Procedures_Grabber
from MachineLearning.Preprocessing import tScore_Scraper as tss
from MongoInterface import mongo as mng
from matplotlib import pyplot as plt
from difflib import get_close_matches

def Get_Clinicals(clinical_para="DRE", telo_para="maxInt", tpoint="+00m"):
    patients = mng.getPatientList()
    # Because gleason, #cores occurs within the 'procedures' extra steps are needed.
    if clinical_para.lower() == "gleason" or clinical_para.lower() == "primary/secondary" or clinical_para.lower() == 'cores':
        procedures = [mng.retrieveDoc(patientnum)['procedures'] for patientnum in patients]
        clinicals = [Procedures_Grabber(procedure, clinical_para) for procedure in procedures]
    else:
        # get basic clinicals
        clinicals = [str(mng.retrieveDoc(patientnum)[clinical_para]).replace('nan', 'Unknown').capitalize() for patientnum in patients]
    # preprocessing steps
    if clinical_para.lower() == "dre":
        # perform DRE preprocessing (collapsing strings)
        clinicals = [dre(clinical)[0] for clinical in clinicals]
    elif clinical_para.lower() == "tscore":
        clinicals = [tss(clinical) for clinical in clinicals]
    timepoints_raw = [mng.get_filter_by_tPoint(patient, tpoint) for patient in patients]
    # processing to remove missing timepoints
    timepoints = [TimePointer(point, telo_para) for point in timepoints_raw]
    parameters = {'clinical_parameter':clinical_para, 'teloview_parameter':telo_para, 'timepoint':tpoint}
    return list(zip(patients, clinicals, timepoints)), parameters

def Group_By_Clinical(data):
    group = {}
    # quick removal of data that contains nans
    data = [item for item in data if item[2] != 'nan' and 'nan' not in item[1]]
    clinicals = sorted(set([xxx[1] for xxx in data]))
    for item in clinicals:
        group[item] = [xxx[2] for xxx in data if xxx[1] == item]
    return group

def box_whisker(data, parameters):
    data_to_plot = list(data.values())
    counts = [str(len(instance)) for instance in data_to_plot]
    new = list(data.keys())
    labs = [str(name) + " \n(n=" + str(count) + ")" for name, count in zip(new, counts)]
    plt.boxplot(data_to_plot, labels=labs)
    plt.ylabel(parameters['teloview_parameter'])
    plt.title(parameters['clinical_parameter'] + " " + parameters['timepoint'])
    plt.show()

if __name__ == '__main__':
    clin_p = 'Gleason'
    telo_p = 'numSig'
    possible_clins = get_close_matches(clin_p, ['DRE', 'tScore', 'Cores', "Gleason", "Primary/Secondary"])
    possible_telos = get_close_matches(telo_p,['ACRatio', 'maxInt', 'meanInt', 'nucDia', 'nucVol', 'numSig', 'p1qrt', 'p2qrt', 'p3qrt', 'p4qrt', 'peakNumSig', 'prAgg', 'prDist', 'sigPerVol'])
    data, parameters = Get_Clinicals(possible_clins[0], possible_telos[0], '+00m')

    groups = Group_By_Clinical(data)
    box_whisker(groups, parameters)