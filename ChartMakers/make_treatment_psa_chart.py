import os
from ChartMakers.chart_maker import calculate_axes, createTextBox, getTrxDates
from DB_DIR import mongo as mng
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


para_dict = {"nucVol":"Mean Nuclear Volume", "prAgg":"Aggregates: Percentage of All Telomere Signals",
                 "nucDia":"Mean Nuclear Diameter", "meanInt":"Mean Intensity of All Telomere Signals", "prDist": "Mean Percent Distance from Nuclear Centre",
                 "ACRatio": "A/C Ratio", "sigPerVol":"Signal Number per Nuclear Volume (um e2)", "numSig":"Number of Signals per Nucleus"}

patient = "MB0389PR"
para = "meanInt"
project_dir = os.path.expanduser("~/Documents/Lab/Quon Project/parameters")

for patient in mng.getPatientList():
    print(patient)
    try:
        trx_dates = getTrxDates(patient)
    except TypeError:
        continue
    text_box = createTextBox(patient)
    patient_status = text_box.splitlines()[0].split(":")[1].strip()

    for para in para_dict.keys():
        psaDates, psaLevels, parameterDates, parameterLevels, fullDates = calculate_axes(patient, para)
        df_psa = pd.DataFrame({"x_axis": psaDates, "y_axis": psaLevels})
        df_para = pd.DataFrame({"x_axis": parameterDates, "y_axis": parameterLevels})
        fullDates_strs = [date.strftime("%Y-%m-%d") for date in mdates.num2date(fullDates)]
        fig, ax1 = plt.subplots()
        plt.title(patient)
        fig.text(0.9, 0.5, text_box, {'ha': 'center', 'va': 'bottom', 'bbox': {'facecolor': "yellow", "edgecolor": "black", "alpha": 0.5}}, transform=ax1.transAxes)
        color = "red"
        ax1.plot("x_axis", "y_axis", data=df_psa, color=color, marker="o")
        ax1.set_ylabel('PSA Level', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        color = "blue"
        ax2 = ax1.twinx()
        ax2.plot("x_axis", "y_axis", data=df_para, color=color, marker="v")
        ax2.set_ylabel(para_dict[para], color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax1.set_xticks(fullDates)
        ax1.set_xticklabels(fullDates_strs, rotation=90)
        for trx in trx_dates:
            if "cgy" in trx['name'].lower():
                color = "yellow"
            elif "bicalutamide" in trx['name'].lower():
                color = "blue"
            elif "leuprolide" in trx['name'].lower():
                color = "red"
            else:
                color = "green"
            ax1.axvspan(xmin=trx['start'], xmax=trx['end'], label=trx['name'],
                        alpha=0.3, color=color)
            ax1.text((trx['start'] + trx['end'])/2, 0, trx['name'], {'ha': 'center', 'va': 'bottom', 'bbox': {'facecolor': color, "alpha": 0.5}}, rotation=90)
        # plt.show()
        fig.set_size_inches(18.5, 10.5)
        needed_dir = os.path.join(project_dir, para)
        os.makedirs(needed_dir, exist_ok=True)
        plt.savefig(os.path.join(needed_dir, patient + "-" + para + ".png"), dpi=100)
        if patient_status.lower() == 'deceased':
            os.makedirs(os.path.join(project_dir, patient_status, para), exist_ok=True)
            plt.savefig(os.path.join(project_dir, patient_status, para, patient + "-" + para + ".png"), dpi=100)
        plt.close()
