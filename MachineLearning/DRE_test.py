
from MachineLearning.Preprocessing import DRE_Closest_Result as dre
from MongoInterface import mongo as mng
from matplotlib import pyplot as plt

def Get_DREs(clinical_para="DRE", telo_para="maxInt", tpoint="+00m"):
    patients = mng.getPatientList()
    if clinical_para == "DRE":
        clinicals = [dre(str(mng.retrieveDoc(patientnum)['DRE']).replace('nan', 'Unknown').capitalize())[0] for patientnum in
            patients]
    else:
        clinicals = [str(mng.retrieveDoc(patientnum)[clinical_para]).replace('nan', 'Unknown').capitalize() for patientnum in patients]
    print(clinicals)
    timepoints = [mng.get_filter_by_tPoint(patient, tpoint)[list(mng.get_filter_by_tPoint(patient, tpoint).keys())[0]][telo_para] for patient in patients]
    parameters = {'clinical_parameter':clinical_para, 'teloview_parameter':telo_para, 'timepoint':tpoint}
    return list(zip(patients, clinicals, timepoints)), parameters
    #data = list(zip(patients, clinicals, timepoints))

def Group_By_Clinical(data):
    group = {}
    clinicals = set([xxx[1] for xxx in data])
    for item in clinicals:
        group[item] = [xxx[2] for xxx in data if xxx[1] == item]
    return group


def box_whisker(data, parameters):
    data_to_plot = list(data.values())
    plt.boxplot(data_to_plot, labels=list(data.keys()))
    plt.ylabel(parameters['teloview_parameter'])
    plt.title(parameters['clinical_parameter'] + " " + parameters['timepoint'])
    #plt.xticks(list(data.keys()))
    plt.show()

if __name__ == '__main__':
    data, parameters = Get_DREs('status', 'nucDia', '+00m')
    groups = Group_By_Clinical(data)
    box_whisker(groups, parameters)