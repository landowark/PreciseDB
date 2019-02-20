import pymongo as pmg
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


analysis_type = "Exclusion" # "Sensitivity"
cutoff = ".1" # .5
PSA_file = os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project/Mary's Analyses", analysis_type + ".xlsx")
adtrad = "psa6mafcompleterad" # "psa6moafadt"

def get_count_quartiles(filtDict):
    sigNums = [filtDict['images'][image]['sigNum'] for image in filtDict['images'].keys()]
    avg = np.mean(sigNums)
    dest = np.histogram(sigNums, 4)
    print(dest)
    quart_list = []
    for item in np.ravel(dest)[0]:
        quart_list.append(float((item / len(sigNums)) * 100))
    return {"q1": float(quart_list[0]), "q2": float(quart_list[1]),
            "q3": float(quart_list[2]), "q4": float(quart_list[3]), 'avg':avg, 'all':sigNums}


def make_boxplot(master):

    above = [master[patient]['all'] for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
    above_labels = [patient for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
    #above = [item for sublist in above for item in sublist]
    below = [master[patient]['all'] for patient in master.keys() if master[patient]['threshold'] == "<0.1"]
    below_labels = [patient for patient in master.keys() if master[patient]['threshold'] == "<0.1"]
    # below = [item for sublist in below for item in sublist]
    # data = above + below
    # print(above)
    # plt.boxplot(data,  showfliers=False)
    # plt.show()
    fig, axes = plt.subplots(1, 2, sharey=True)
    axes[0].boxplot(above, labels=above_labels, showfliers=False)
    axes[0].set_title("Post-RT PSA >=0.1 ng/mL")
    for tick in axes[0].get_xticklabels():
        tick.set_rotation(90)
    axes[1].boxplot(below, labels=below_labels, showfliers=False)
    axes[1].set_title("Post-RT PSA <0.1 ng/mL")
    for tick in axes[1].get_xticklabels():
        tick.set_rotation(90)
    fig.suptitle('Number of telomere signals per cell', fontsize=16)
    plt.show()



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
            master[patient] = get_count_quartiles(filtDict)
            index = df.loc[df['pt_id']==pd_patient].index[0]
            master[patient]["threshold"] = df.loc[index].at[adtrad]
        except IndexError:
            continue
    for patient in patient_list:
        check_condition1 = master[patient]['q1'] == 0.0 and master[patient]['q2'] == 0.0 and master[patient]['q3'] == 0.0 and master[patient]['q4'] == 0.0
        check_condition2 = master[patient]['q1'] == '' and master[patient]['q2'] == '' and master[patient]['q3'] == '' and master[patient]['q4'] == ''
        #print(patient, master[patient])
        if check_condition1 or check_condition2 or "threshold" not in list(master[patient].keys()):
            del master[patient]
    #print(master['MB0431PR'])
    writer2 = pd.ExcelWriter(os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "signum_quartiles.xlsx"))
    df2 = pd.DataFrame(master).transpose()
    df2.to_excel(writer2, sheet_name="master", engine='xlsxwriter')
    writer2.close()
    make_boxplot(master)



if __name__ == "__main__":
    main()