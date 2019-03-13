from io import BytesIO
import pymongo as pmg
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy import stats
import seaborn as sns


analysis_type = "Exclusion" # "Sensitivity"
cutoff = ".1" # 0.5
PSA_file = os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project/Mary's Analyses", analysis_type + ".xlsx")
adtrad = "psa6mafcompleterad" #"psa6moafadt" #


def check_for_threshold(master, patient):
    if "threshold" not in list(master[patient].keys()):
        return True
    else:
        return False


def get_count_quartiles(filtDict, parameter: str):
    para_measure = [filtDict['images'][image][parameter] for image in filtDict['images'].keys()]
    avg = np.mean(para_measure)
    dest = np.histogram(para_measure, 4)
    quart_list = [float((item / len(para_measure)) * 100) for item in np.ravel(dest)[0]]
    quart_1 = [measure for measure in para_measure if measure >= dest[1][0] and measure < dest[1][1]]
    quart_2 = [measure for measure in para_measure if measure >= dest[1][1] and measure < dest[1][2]]
    quart_3 = [measure for measure in para_measure if measure >= dest[1][2] and measure < dest[1][3]]
    quart_4 = [measure for measure in para_measure if measure >= dest[1][3] and measure < dest[1][4]]
    return {"quartile_1":quart_1, "quartile_2": quart_2, "quartile_3":quart_3, "quartile_4":quart_4,
            "q1_percent": float(quart_list[0]), "q2_percent": float(quart_list[1]),
            "q3_percent": float(quart_list[2]), "q4_percent": float(quart_list[3]), 'avg':avg, 'all':para_measure}


def make_rank_chart(master, parameter: str):

    if adtrad == "psa6moafadt":
        subtitle_adtrad = "ADT"
    elif adtrad == "psa6mafcompleterad":
        subtitle_adtrad = "RT"
    df['<0.1'] = pd.Series([item2 for sublist2 in below for item2 in sublist2])
    df['>=0.1'] = pd.Series([item1 for sublist1 in above for item1 in sublist1])
    # df[(np.abs(stats.zscore(df)) > 2).all(axis=1)]
    # print(df)
    # ax = sns.violinplot(data=df, inner=None)
    fig, ax =plt.subplots(figsize=(15,15))
    sns.swarmplot(data=df, ax=ax)
    plt.title(parameter)
    imgdata = BytesIO()
    plt.savefig(imgdata, format="png")
    plt.clf()
    imgdata.seek(0)
    return imgdata


def make_boxplot(master, parameter: str):
    above = [master[patient]["all"] for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
    above_labels = [patient for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
    below = [master[patient]["all"] for patient in master.keys() if master[patient]['threshold'] == "<0.1"]
    below_labels = [patient for patient in master.keys() if master[patient]['threshold'] == "<0.1"]

    if adtrad == "psa6moafadt":
        subtitle_adtrad = "ADT"
    elif adtrad == "psa6mafcompleterad":
        subtitle_adtrad = "RT"
    fig1, axes1 = plt.subplots(1, 2, sharey=True, gridspec_kw = {'width_ratios':[1, 3]}, figsize=(15,15))
    flat = [[item1 for sublist1 in above for item1 in sublist1], [item2 for sublist2 in below for item2 in sublist2]]
    axes1[0].boxplot(above, labels=above_labels, showfliers=False)
    axes1[0].set_title("Post-{} PSA >=0{} ng/mL".format(subtitle_adtrad, cutoff))
    for tick in axes1[0].get_xticklabels():
        tick.set_rotation(90)
    axes1[1].boxplot(below, labels=below_labels, showfliers=False)
    axes1[1].set_title("Post-{} PSA <0{} ng/mL".format(subtitle_adtrad, cutoff))
    for tick in axes1[1].get_xticklabels():
        tick.set_rotation(90)
    fig1.suptitle("Quartiles of {} per cell.".format(parameter), fontsize=16)
    imgdata1 = BytesIO()
    plt.savefig(imgdata1, format="png")
    plt.clf()
    imgdata1.seek(0)
    fig2, axes2 = plt.subplots()
    axes2.boxplot(flat, labels=[">=0.1", "<0.1"], showfliers=False)
    imgdata2 = BytesIO()
    plt.savefig(imgdata2, format="png")
    plt.clf()
    imgdata2.seek(0)
    return imgdata1, imgdata2


def make_quartile_plot(master, parameter):
    img_dict = {}
    quart_list = ['quartile_1', 'quartile_2', 'quartile_3', 'quartile_4']
    percent_list = ["q1_percent", "q2_percent", "q3_percent", "q4_percent"]
    for quart in quart_list:
        # print("Running {} chart for {}".format(quart, parameter))
        q_above = [master[patient][quart] for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
        q_below = [master[patient][quart] for patient in master.keys() if master[patient]['threshold'] == "<0.1"]
        q_above = np.array([item1 for sublist1 in q_above for item1 in sublist1])
        q_below = np.array([item2 for sublist2 in q_below for item2 in sublist2])
        above_mean = np.mean(q_above)
        below_mean = np.mean(q_below)
        above_stde = stats.sem(q_above)
        below_stde = stats.sem(q_below)
        plt.clf()
        plt.errorbar(x=[">=0.1", "<0.1"], y=[above_mean, below_mean], yerr=[above_stde, below_stde], fmt='o')
        plt.title(quart, loc='center')
        imgdata = BytesIO()
        plt.savefig(imgdata, format="png")
        plt.clf()
        imgdata.seek(0)
        img_dict[quart] = imgdata
    for percent in percent_list:
        # print("Running {} chart for {}".format(percent, parameter))
        q_above = [master[patient][percent] for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
        q_below = [master[patient][percent] for patient in master.keys() if master[patient]['threshold'] == "<0.1"]
        q_above = np.array(q_above)
        q_below = np.array(q_below)
        above_mean = np.mean(q_above)
        below_mean = np.mean(q_below)
        above_stde = stats.sem(q_above)
        below_stde = stats.sem(q_below)
        plt.clf()
        plt.errorbar(x=[">=0.1", "<0.1"], y=[above_mean, below_mean], yerr=[above_stde, below_stde], fmt='o')
        plt.title(percent, loc='center')
        imgdata = BytesIO()
        plt.savefig(imgdata, format="png")
        plt.clf()
        imgdata.seek(0)
        img_dict[percent] = imgdata
    return img_dict


def main():
    used_db = "quon_actual"
    df = pd.read_excel(PSA_file, sheet_name=cutoff + " cutoff")
    db = pmg.MongoClient().get_database(used_db).patient
    patient_list = [doc['_id'] for doc in db.find().batch_size(10)]
    para = ["ACRatio", "meanDist", "meanIntAll", "meanIntNorm", "nucDia", "nucVol", "prcAgg", "sigNum", "sigPerVol"]
    for parameter in para:
        print("Running parameter: {}".format(parameter))
        master = {}
        for patient in patient_list:
            pd_patient = int(patient[3:-2])
            try:
                doc = db.find_one({'_id': patient})
                for filter in list(doc['filters'].keys()):
                    if doc['filters'][filter]['tPoint'] == "+00m":
                        filtDict = doc['filters'][filter]
                        master[patient] = get_count_quartiles(filtDict, parameter)
                        index = df.loc[df['pt_id']==pd_patient].index[0]
                        master[patient]["threshold"] = df.loc[index].at[adtrad]
                    else:
                        filtDict = {}
                        continue
            except IndexError:
                continue
            except KeyError:
                continue
        for patient in patient_list:
            try:
                check_condition1 = master[patient]['q1_percent'] == 0.0 and master[patient]['q2_percent'] == 0.0 and master[patient]['q3_percent'] == 0.0 and master[patient]['q4_percent'] == 0.0
                check_condition2 = master[patient]['q1_percent'] == '' and master[patient]['q2_percent'] == '' and master[patient]['q3_percent'] == '' and master[patient]['q4_percent'] == ''
                check_condition3 = check_for_threshold(master, patient)
                check_condition4 = math.isnan(master[patient]['q1_percent']) and math.isnan(master[patient]['q2_percent']) and math.isnan(master[patient]['q3_percent']) and math.isnan(master[patient]['q4_percent'])
                if check_condition1 or check_condition2 or check_condition3 or check_condition4:
                    del master[patient]
            except KeyError:
                continue
        # try:
        df2 = pd.DataFrame(master).transpose()
        df2.index.name = "Patient"
        df3 = pd.DataFrame()
        above = [master[patient]['all'] for patient in master.keys() if master[patient]['threshold'] == ">=0.1"]
        below = [master[patient]['all'] for patient in master.keys() if master[patient]['threshold'] == "<0.1"]
        plot1, plot2 = make_boxplot(master, parameter)
        plot3 = make_rank_chart(master, parameter)
        img_dict = make_quartile_plot(master, parameter)
        writer2 = pd.ExcelWriter(os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "{}_quartiles.xlsx".format(parameter)))

        df2.to_excel(writer2, sheet_name="master", engine='xlsxwriter')
        workbook = writer2.book
        worksheet1 = writer2.sheets["master"]
        worksheet2 = workbook.add_worksheet("flattened")
        worksheet3 = workbook.add_worksheet("quartiles_raw")
        worksheet4 = workbook.add_worksheet("quartiles_percentage")
        worksheet5 = workbook.add_worksheet("swarm")
        if plot1 != None:
            worksheet1.insert_image(0, 9, "", {'image_data': plot1})
        worksheet2.insert_image(00, 00, "", {'image_data': plot2})
        worksheet3.insert_image(00, 00, "", {'image_data': img_dict['quartile_1']})
        worksheet3.insert_image(00, 10, "", {'image_data': img_dict['quartile_2']})
        worksheet3.insert_image(25, 00, "", {'image_data': img_dict['quartile_3']})
        worksheet3.insert_image(25, 10, "", {'image_data': img_dict['quartile_4']})
        worksheet4.insert_image(00, 00, "", {'image_data': img_dict['q1_percent']})
        worksheet4.insert_image(00, 10, "", {'image_data': img_dict['q2_percent']})
        worksheet4.insert_image(25, 00, "", {'image_data': img_dict['q3_percent']})
        worksheet4.insert_image(25, 10, "", {'image_data': img_dict['q4_percent']})
        worksheet5.insert_image(00, 00, "", {'image_data': plot3})
        writer2.close()

        # except:
        #     continue


if __name__ == "__main__":
    main()