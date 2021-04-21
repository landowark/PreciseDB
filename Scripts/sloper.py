# -*- coding: utf-8 -*-
"""
Created on Mon Mar 9 12:18:07 2015
This is the script I created to perform the telomere bin count
difference between patient samples and return a curve used to
compare change between timepoints.
@author: Landon Wark
"""
#imports
import scipy as sp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from DB_DIR import menu_items as fg #my custom file retrieval module
from scipy.stats import ks_2samp #Kolmogrov-Smirnov module
import os

home_dir = os.path.join(os.path.expanduser("~"), "Documents/Lab/Quon Project")


def ctc_parser(data):
    #skips over any lymphocyte data if present
    start_list = list(data.columns.values)
    for item in start_list:
        if 'lymp' in item:
            start_list.remove(item)
    return(start_list)


def data_gen(samples, data):
    #pulls out intensity bin data
    df = pd.DataFrame(data['Intensity Bins'])
    for item in samples:
        df[item] = data[item]
    return(df)


def comper(bins, AA, BB):
    #gets the maximum count in a bin and creates an array of differences iterating until both histograms reach 0
    aa = list(AA)
    bb = list(BB)

    maxIndAA = np.argmax(aa)
    maxIndBB = np.argmax(bb)
    #print(maxIndAA, maxIndBB)
    dif_array = []
    if min(maxIndAA, maxIndBB) == maxIndAA:
        sub = aa
    else:
        sub = bb
    #print(range(min(maxIndAA, maxIndBB), len(bins)))
    for jjj in range(min(maxIndAA, maxIndBB), len(bins)):
        #print(bb[jjj], aa[jjj])
        diff = bb[jjj] - aa[jjj]
        dif_array.append(diff)
        if sub[jjj] == 0:
            break
    return(dif_array)


def graph(bins, dif_array, series1, series2, patName):
    #format data
    #print(series1, series2)
    #series1 = series1[0:-10]
    #series2 = series2[0:-10]
    try:
        dif_array = np.array(dif_array).astype(float)
        dif_array = dif_array[~np.isnan(dif_array)]
        bins = bins[0:len(dif_array)]
        #print(dif_array)
        #find line formula
        fp1, residuals, rank, sv, rcond = sp.polyfit(bins, dif_array, 2, full=True)
        print("Line equation: %.3e(x^2) + %.3e(x)" % (fp1[0], fp1[1]))
        # This is the relevant number for this project.
        f1 = sp.poly1d(fp1)
        fx = sp.linspace(min(bins), max(bins)) # generate X-values for plotting
        #make plot
        plt.scatter(bins, dif_array)
        plt.title((series2 + " vs. " + series1))
        plt.xlabel("Signal Intensity")
        plt.ylabel("Change in count")
        plt.autoscale(tight=True)
        plt.grid(True)
        plt.plot(fx, f1(fx), linewidth=4)
        plt.legend(["m = %.3e(x^2) + %.3e(x)" % (fp1[0], fp1[1])], loc="lower center")
        plt.savefig(os.path.join(home_dir, patName, series2 + " vs " + series1))
        #plt.show()
        plt.close()
        s_name = series2 + " vs " + series1
        return float(fp1[1]), s_name, fp1, bins
    except ValueError as e:
        print(patName, series2, series1)
        raise e


def kstest(x, y):
    #perform ks_test
    result = ks_2samp(x,y)
    print('KS result: KS = %.3f, p = %.3e' % result)
    return(result[1])


def bar_chart(series, slopes, patName):
    slopes = [float(num) for num in slopes]
    plt.bar(series, slopes)
    plt.title(patName)
    plt.savefig(os.path.join(home_dir, patName, patName + ".tif"), format='tif')
    plt.close()



def csv_writer(big_list, pat_name):
    #write results to file
    headers = ("Series", "Slope", "KS-p")
    pat_name = pat_name + '.xlsx'
    datas = pd.DataFrame(big_list, columns=headers)
    writer = pd.ExcelWriter(os.path.join(home_dir, os.path.splitext(pat_name)[0], pat_name), engine='xlsxwriter')
    datas.to_excel(writer, 'Data')
    writer.save()
    writer.close()
    bar_chart(list(datas['Series']), list(datas['Slope']), os.path.splitext(pat_name)[0])


def main(df: pd.DataFrame, pat_name: str):
    try:
        bins = df.index.values
        slope_list = []
        ks_list = []
        name_list = []
        samples = ctc_parser(df)
        if not os.path.exists(os.path.join(home_dir, os.path.splitext(pat_name)[0])):
            os.makedirs(os.path.join(home_dir, os.path.splitext(pat_name)[0]))
        for iii in range(0, len(samples)-1):
            try:
                #print(samples[iii])
                AA = df[samples[iii]]
                BB = df[samples[iii+1]]
                #print(list(BB))
                ks_result = kstest(AA, BB)
                dif_array = comper(bins,AA,BB)
                slope, nam, func, bins = graph(bins, dif_array, samples[iii], samples[iii+1], pat_name)
                slope_list.append(slope)
                ks_list.append(ks_result)
                name_list.append(nam)
            except TypeError:
                continue
        slope_list = np.array(slope_list, dtype=float)
        big_list = np.dstack((name_list, slope_list, ks_list))
        csv_writer(np.squeeze(big_list, axis=0), pat_name)
        return big_list
    except FileNotFoundError as e:
        print(pat_name)
        print("Operation cancelled: No file available.")
        raise e