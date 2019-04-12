from io import BytesIO
import pymongo as pmg
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
from scipy import stats
import seaborn as sns


para_dict = {"nucVol":"Mean Nuclear Volume", "prcAgg":"Aggregates: Percentage of All Telomere Signals",
                 "nucDia":"Mean Nuclear Diameter", "meanIntNorm":"Mean Intensity of Non-Aggregate Telomere Signals",
                 "meanIntAll":"Mean Intensity of All Telomere Signals", "meanDist": "Mean Percent Distance from Nuclear Centre",
                 "ACRatio": "A/C Ratio", "sigPerVol":"Signal Number per Nuclear Volume (um e2)", "sigNum":"Number of Signals per Nucleus"}


def reject_outliers(data, m=2):
    data = np.array(data)
    return data[abs(data - np.mean(data)) < m * np.std(data)]

def check_for_threshold(master, patient):
    if "threshold" not in list(master[patient].keys()):
        return True
    else:
        return False


def get_count_quartiles(filtDict, parameter: str):
    para_measure = [filtDict['images'][image][parameter] for image in filtDict['images'].keys()]
    para_measure = reject_outliers(para_measure, 2)
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


def make_swarm_chart(master, parameter: str, adtrad, cutoff):
    df = pd.DataFrame()
    above = [master[patient]["all"] for patient in master.keys() if master[patient]['threshold'] == ">=0{}".format(cutoff)]
    below = [master[patient]["all"] for patient in master.keys() if master[patient]['threshold'] == "<0{}".format(cutoff)]
    if adtrad == "psa6moafadt":
        subtitle_adtrad = "ADT"
    elif adtrad == "psa6mafcompleterad":
        subtitle_adtrad = "RT"
    df['>=0'.format(cutoff)] = pd.Series([item1 for sublist1 in above for item1 in sublist1])
    df['<0'.format(cutoff)] = pd.Series([item2 for sublist2 in below for item2 in sublist2])
    fig1, ax1 =plt.subplots(figsize=(15,15))
    sns.swarmplot(data=df, ax=ax1)
    plt.title(parameter)
    imgdata = BytesIO()
    plt.savefig(imgdata, format="png")
    plt.clf()
    imgdata.seek(0)
    return imgdata


def make_boxplot(master, parameter: str, adtrad, cutoff):
    above = [master[patient]["all"] for patient in master.keys() if master[patient]['threshold'] == ">=0{}".format(cutoff)]
    above_labels = [patient for patient in master.keys() if master[patient]['threshold'] == ">=0{}".format(cutoff)]
    below = [master[patient]["all"] for patient in master.keys() if master[patient]['threshold'] == "<0{}".format(cutoff)]
    below_labels = [patient for patient in master.keys() if master[patient]['threshold'] == "<0{}".format(cutoff)]
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
    axes2.boxplot(flat, labels=[">=0{}".format(cutoff), "<0{}".format(cutoff)], showfliers=False)
    imgdata2 = BytesIO()
    plt.savefig(imgdata2, format="png")
    plt.clf()
    imgdata2.seek(0)
    return imgdata1, imgdata2


def make_quartile_plot(master, parameter,cutoff):
    img_dict = {}

    quart_list = ['quartile_1', 'quartile_2', 'quartile_3', 'quartile_4']
    percent_list = ["q1_percent", "q2_percent", "q3_percent", "q4_percent"]
    for quart in quart_list:
        # print("Running {} chart for {}".format(quart, parameter))
        q_above = [master[patient][quart] for patient in master.keys() if master[patient]['threshold'] == ">=0{}".format(cutoff)]
        q_below = [master[patient][quart] for patient in master.keys() if master[patient]['threshold'] == "<0{}".format(cutoff)]
        q_above = np.array([item1 for sublist1 in q_above for item1 in sublist1])
        q_below = np.array([item2 for sublist2 in q_below for item2 in sublist2])
        above_mean = np.mean(q_above)
        below_mean = np.mean(q_below)
        above_stde = stats.sem(q_above)
        below_stde = stats.sem(q_below)
        plt.clf()
        plt.errorbar(x=[">=0{}".format(cutoff), "<0{}".format(cutoff)], y=[above_mean, below_mean], yerr=[above_stde, below_stde], fmt='o')
        plt.title(quart, loc='center')
        imgdata = BytesIO()
        plt.savefig(imgdata, format="png")
        plt.clf()
        imgdata.seek(0)
        img_dict[quart] = imgdata
    for percent in percent_list:
        # print("Running {} chart for {}".format(percent, parameter))
        q_above = [master[patient][percent] for patient in master.keys() if master[patient]['threshold'] == ">=0{}".format(cutoff)]
        q_below = [master[patient][percent] for patient in master.keys() if master[patient]['threshold'] == "<0{}".format(cutoff)]
        q_above = np.array(q_above)
        q_below = np.array(q_below)
        above_mean = np.mean(q_above)
        below_mean = np.mean(q_below)
        above_stde = stats.sem(q_above)
        below_stde = stats.sem(q_below)
        plt.clf()
        plt.errorbar(x=[">=0{}".format(cutoff), "<0{}".format(cutoff)], y=[above_mean, below_mean], yerr=[above_stde, below_stde], fmt='o')
        plt.title(percent, loc='center')
        imgdata = BytesIO()
        plt.savefig(imgdata, format="png")
        plt.clf()
        imgdata.seek(0)
        img_dict[percent] = imgdata
    all_above = [master[patient]["all"] for patient in master.keys() if
               master[patient]['threshold'] == ">=0{}".format(cutoff)]
    all_below = [master[patient]["all"] for patient in master.keys() if
               master[patient]['threshold'] == "<0{}".format(cutoff)]
    all_above = np.array([item1 for sublist1 in all_above for item1 in sublist1])
    all_below = np.array([item2 for sublist2 in all_below for item2 in sublist2])
    above_mean = np.mean(all_above)
    below_mean = np.mean(all_below)
    means = [above_mean, below_mean]

    above_stde = stats.sem(all_above)
    below_stde = stats.sem(all_below)
    errors = [above_stde, below_stde]
    plt.clf()
    fig, axes = plt.subplots(figsize=(15,15))
    axes.bar([1,2], means, yerr=errors, ecolor='black', error_kw=dict(lw=5, capsize=5, capthick=3))
    axes.set_xticks([1,2])
    axes.set_xticklabels([">=0{}".format(cutoff), "<0{}".format(cutoff)])
    axes.set_ylim(top=np.max([(above_mean + above_stde), (below_mean + below_stde)])*2)
    # axes.yaxis.label.set_size(24)
    # axes.xaxis.label.set_size(24)
    # plt.errorbar(x=[">=0{}".format(cutoff), "<0{}".format(cutoff)], y=[above_mean, below_mean],
                 # yerr=[above_stde, below_stde], fmt='o')

    axes.set_title(para_dict[parameter], loc='center', fontsize= 36)
    axes.tick_params(labelsize=24)
    imgdata = BytesIO()
    plt.savefig(imgdata, format="png")
    plt.clf()
    imgdata.seek(0)
    img_dict["All"] = imgdata
    return img_dict


def main():
    analysis_type = ["Exclusion"]#, "Sensitivity"]
    cutoff = [".1"]#, ".5"]
    adtrad = ["psa6mafcompleterad"]#,  "psa6moafadt"]

    used_db = "quon_actual"

    db = pmg.MongoClient().get_database(used_db).patient
    patient_list = [doc['_id'] for doc in db.find().batch_size(10)]
    para = ["ACRatio", "meanDist", "meanIntAll", "meanIntNorm", "nucDia", "nucVol", "prcAgg", "sigNum", "sigPerVol"]
    for rad_type in adtrad:
        print("Running radtype: {}".format(rad_type))
        for c_type in cutoff:
            print("Running cutoff: {}".format(c_type))
            for a_type in analysis_type:
                print("Running analysis type: {}".format(a_type))
                PSA_file = os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project/Mary's Analyses", a_type + ".xlsx")
                print(PSA_file)
                df = pd.read_excel(PSA_file, sheet_name=c_type + " cutoff")
                for parameter in para:
                    file_name = os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "Graphs_{0}_{1}_{2}_{3}quartiles.xlsx".format(a_type, c_type.replace(".", ""), rad_type, parameter))
                    # if not os.path.exists(file_name):
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
                                    master[patient]["threshold"] = df.loc[index].at[rad_type]
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
                    plot1, plot2 = make_boxplot(master, parameter, rad_type, c_type)
                    img_dict = make_quartile_plot(master, parameter, c_type)
                    plot3 = make_swarm_chart(master, parameter, rad_type, c_type)
                    writer2 = pd.ExcelWriter(os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project", "Graphs_{0}_{1}_{2}_{3}quartiles.xlsx".format(a_type, c_type.replace(".", ""), rad_type, parameter)))

                    df2.to_excel(writer2, sheet_name="master", engine='xlsxwriter')
                    workbook = writer2.book
                    worksheet1 = writer2.sheets["master"]
                    worksheet2 = workbook.add_worksheet("flattened")
                    worksheet3 = workbook.add_worksheet("quartiles_raw")
                    worksheet4 = workbook.add_worksheet("quartiles_percentage")
                    worksheet5 = workbook.add_worksheet("swarm")
                    worksheet6 = workbook.add_worksheet("All_mean")
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
                    worksheet6.insert_image(00, 00, "", {'image_data': img_dict['All']})
                    writer2.close()

                    # except ValueError as e:
                    #     print("Oops on : {0}_{1}_{2}_{3}".format(a_type, c_type.replace(".", ""), rad_type, parameter) )
                    #     print(str(e.__traceback__.tb_next.tb_lineno))
                    #     continue
                    # else:
                    #     print("File {} exists, skipping.".format(file_name))


if __name__ == "__main__":
    main()