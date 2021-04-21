import logging
import logging.handlers
import os
from pathlib import Path
import pandas as pd
from tkinter import *
from tkinter import filedialog
import numpy as np
from lxml import etree as ET
import zipfile
import sys


'''
Take directory with xlsx files and return telom/combgraphs
'''

class Application(Frame):

    def createWidgets(self):
        self.telomgraphBTN = Button(self, text="Telomgraph", command=telomgraph_main)
        self.telomgraphBTN.pack(side='top')
        # self.telomgraphBTN.place(relx=0.5, rely=0.5)
        self.combgraphBTN = Button(self, text="Combgraph", command=combgraph_main)
        self.combgraphBTN.pack(side='bottom')
        # self.combgraphBTN.place(relx=0.7, rely=0.7)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack(side='top')
        self.place(relx=0.4, rely=0.4)
        self.createWidgets()


def setup_logging():
    global logger
    logger = logging.getLogger("intensity_calcs")
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.handlers.RotatingFileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'IntCalc.log'), mode='a', maxBytes=100000, backupCount=3, encoding=None, delay=False)
    fh.setLevel(logging.DEBUG)
    fh.name = "File"
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.name = "Stream"
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(ch_formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.debug("Starting Run.")


def user_get_dir():
    # create folder selection dialog
    root = Tk()
    root.withdraw()
    filename = filedialog.askdirectory(title="Select main directory", initialdir=os.path.expanduser("~"))
    root.destroy()
    return filename


def get_cell_dirs(main_dir_path: str):
    # Gets sorted list of parent directories of xlsx files
    return sorted(list(set([os.path.dirname(item) for item in Path(main_dir_path).glob("**/*.xlsx")])))


def get_files_in_dir(directory: str, mode:str='telomgraph'):
    # Gets sorted list of all xlsx files recursively in directory
    return_list = []
    for file in sorted(list(set([item for item in Path(directory).glob("*.xlsx")]))):
        xml = [item.text for item in ET.fromstring(zipfile.ZipFile(file).open('docProps/core.xml').read())]
        if mode == 'telomgraph':
            try:
                if 'telomgraph' not in xml:
                    return_list.append(file)
            except IndexError:
                continue
        elif mode == 'combgraph':
            try:
                if 'telomgraph' in xml:
                    logger.debug("Found xml value: {} in {}. Adding to list of files".format(xml, file))
                    return_list.append(file)
            except IndexError:
                continue
    if return_list != []:
        return return_list
    else:
        return None


def get_bins_from_ints(intensities_single: list):
    logger.debug("Building bins.")
    # calculates bins from intensity list.
    max_bin = round(np.max(intensities_single), -3)
    try:
        bins = np.arange(0, max_bin+1000, 1000)
        intensity_bins = np.histogram(intensities_single, bins)
        return pd.DataFrame(intensity_bins[0], bins[:-1], columns=['Number of Telomeres'])
    except Exception as e:
        logger.debug(e)


def get_summary_data(df, file_name: str):
    logger.debug("Building summary.")
    summary_dict = {}
    summary_dict['Nuclear volume'] = df.iloc[df.index[df['spots number'] == 'nuclear volume:'] + 1]['spots number'].iloc[0]
    summary_dict['Cell #'] = file_name
    summary_dict['Total # of signals'] = df['x'][df['x'].notnull()].__len__()
    summary_dict['Total # of aggregates'] = df['Aggregates'][df['Aggregates'] > 0].__len__()
    summary_dict['Nuclear volume'] = \
    summary_dict['a/c ratio'] = df.iloc[df.index[df['spots number'] == 'a/c-ratio:'] + 1]['spots number'].iloc[0]
    summary_dict['Av.Int. all signals'] = df.iloc[df.index[df['spots number'] == 'Average intensity all telomeres:'] + 1]['spots number'].iloc[0]
    summary_dict['Total intensity'] = np.sum(df['Intensity'])
    return summary_dict


def get_percentage_data(df) -> pd.DataFrame:
    logger.debug("Building percentage data.")
    out_df = {}
    out_df['Percentage of cells with aggregates:'] = (df[df['Total # of aggregates'] > 0].__len__() / df.__len__()) * 100
    out_df['Average number of telomeres per cell:'] = np.mean(df['Total # of signals'])
    out_df['Average number of aggregates per cell:'] = np.mean(df['Total # of aggregates'])
    out_df['Average of nuclear volume:'] = np.mean(df['Nuclear volume'])
    out_df = pd.DataFrame(out_df, index=[0])
    return out_df.transpose()


def build_telodf_from_excel(xlsx_files: list) -> dict:
    logger.debug("Making dataframes.")
    telom_dict = {}
    telom_dict['bins'] = pd.DataFrame()
    telom_dict['summary'] = pd.DataFrame(columns=['Cell #', 'Total # of signals', 'Total # of aggregates', 'a/c ratio', 'Av.Int. all signals', 'Total intensity', 'Nuclear volume'])
    telom_dict['percentage'] = pd.DataFrame()
    telom_dict['all_intensities'] = pd.DataFrame()
    telom_dict['intensities_single'] = pd.Series()
    telom_dict['quartiles'] = pd.DataFrame(columns=['Min', 'Q1', 'Median', 'Q3', 'Max'])
    filenames = []
    for file in xlsx_files:
        filenames.append(os.path.basename(file))
        xl_data = pd.read_excel(file)
        try:
            ints = xl_data['Intensity'][xl_data['Intensity'].notnull()].astype(int)
        except KeyError:
            logger.error("Improperly formatted Excel file: {}, skipping".format(file))
            continue
        quart_series = pd.Series({
                                'Min':np.min(ints),
                                'Q1': np.percentile(ints, [25])[0],
                                'Median':np.percentile(ints, [50])[0],
                                'Q3':np.percentile(ints, [75])[0],
                                'Max':np.max(ints)
        })
        quart_series.name = os.path.basename(file)
        telom_dict['quartiles'] = telom_dict['quartiles'].append(quart_series)
        telom_dict['summary'] = telom_dict['summary'].append(get_summary_data(xl_data, file.name), ignore_index=True)
        telom_dict['all_intensities'] = telom_dict['all_intensities'].append(ints)
        telom_dict['intensities_single'] = telom_dict['intensities_single'].append(ints)
    if telom_dict['intensities_single'].empty:
        logger.error("This folder yielded an empty dataframe.")
        return None
    telom_dict['bins'] = get_bins_from_ints(telom_dict['intensities_single'].tolist())
    telom_dict['all_intensities'] = telom_dict['all_intensities'].T
    telom_dict['all_intensities'].columns = filenames
    telom_dict['intensities_single'] = pd.DataFrame(telom_dict['intensities_single'])
    telom_dict['percentage'] = get_percentage_data(telom_dict['summary'])
    return telom_dict


def build_comb_df_from_excel(xlsx_files: list) -> dict:
    logger.debug("Making dataframes.")
    comb_dict = {}
    comb_dict['bins'] = pd.DataFrame()
    comb_dict['all_intensities'] = pd.DataFrame()
    filenames = []
    for file in xlsx_files:
        filenames.append(os.path.basename(file))
        bin_xl_data = pd.read_excel(file, sheet_name="bins")['Number of Telomeres'].astype(int)
        int_xl_data = pd.read_excel(file, sheet_name="intensities_single", header=None).astype(int)
        comb_dict['bins'] = pd.concat([comb_dict['bins'], bin_xl_data], axis=1, sort=False)
        comb_dict['all_intensities'] = pd.concat([comb_dict['all_intensities'], int_xl_data], axis=1, sort=False)
    comb_dict['bins'].columns = filenames
    if sys.platform == 'win32':
        comb_dict['bins'].index = comb_dict['bins'].index.values * 1000
    comb_dict['all_intensities'].columns = filenames
    return comb_dict


def teloChartMaker(bins_df, workbook, sampleName):
    bin_values = pd.DataFrame(bins_df.index.values, columns=['bins'])
    bin250labels = bin_values['bins']
    bin250max = bin250labels[pd.notnull(bin250labels)].idxmax()
    bin250chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
    bin250chart.add_series({
        'categories': ['bins', 1, 0, bin250max, 0],
        'values': ['bins', 1, 1, bin250max, 1],
        'line': {'color': 'red'},
        'marker': {'type': 'diamond', 'border': {'color': 'red'}, 'fill': {'color': 'red'}, }
    })
    bin250chart.set_x_axis({
        'name': 'Intensity[a.u.]',
        'name_font': {'size': 14, 'bold': True},
    })
    bin250chart.set_y_axis({
        'name': 'Number of Telomeres',
        'name_font': {'size': 14, 'bold': True},
    })
    bin250chart.set_title({'name': sampleName})
    bin250chart.set_legend({'none': True})
    bin250chartsheet = workbook.add_chartsheet()
    bin250chartsheet.set_chart(bin250chart)


def combChartMaker(bins_df, workbook, sampleName):
    bin_values = pd.DataFrame(bins_df.index.values, columns=['bins'])
    bin250labels = bin_values['bins'].astype('int')
    bin250max = bin250labels[pd.notnull(bin250labels)].idxmax()
    colors = ['red', 'blue', 'green', 'orange', 'magenta', 'yellow']
    bin250chart = workbook.add_chart({'type': 'scatter', 'subtype': 'straight_with_markers'})
    # Create a series for each column in dataframe
    for xxx, col in enumerate(bins_df):
        sample = bins_df[col].name

        bin250chart.add_series({
            'name': sample,
            'categories': ['bins', 1, 0, bin250max, 0],
            'values': ['bins', 0, xxx + 1, bin250max, xxx + 1],
            'line': {'color': colors[xxx]},
            'marker': {'type': 'diamond', 'border': {'color': colors[xxx]}, 'fill': {'color': colors[xxx]}, }
        })
    bin250chart.set_x_axis({
        'name': 'Intensity[a.u.]',
        'name_font': {'size': 14, 'bold': True},
    })
    bin250chart.set_y_axis({
        'name': 'Number of Telomeres',
        'name_font': {'size': 14, 'bold': True},
    })
    bin250chart.set_title({'name': sampleName})
    bin250chart.set_legend({'position': 'bottom'})
    bin250chartsheet = workbook.add_chartsheet(name='COMPARISON')
    bin250chartsheet.set_chart(bin250chart)


def boxwhiskerChartMaker(all_intensities_df, workbook, sampleName):
    # todo make a boxandwhisker plot maker somehow.
    boxchart = workbook.add_chart({'type': 'stock'})


def telomgraph_write(telom_dict, directory):
    main_output_name = os.path.basename(directory)
    if main_output_name == "Teloview_results":
        main_output_name = os.path.basename(os.path.dirname(directory))
        logger.debug("Got generic teloview folder, converting to {}".format(main_output_name))
    outpath = os.path.join(os.path.dirname(directory), main_output_name + "_telomgraph.xlsx")
    logger.debug("Attempting xlsx write to {}.".format(outpath))
    writer = pd.ExcelWriter(outpath, engine='xlsxwriter')
    workbook = writer.book
    workbook.set_properties({'keywords':'telomgraph'})
    for key in telom_dict.keys():
        if key in ["bins", "summary", "quartiles"]:
            telom_dict[key].to_excel(writer, sheet_name=key)
        elif key in ['percentage']:
            telom_dict[key].to_excel(writer, sheet_name=key, header=False)
        elif key in ['summary', 'all_intensities']:
            telom_dict[key].to_excel(writer, sheet_name=key, index=False)
        else:
            telom_dict[key].to_excel(writer, sheet_name=key, header=False, index=False)
    teloChartMaker(telom_dict['bins'], workbook, main_output_name)
    # boxwhiskerChartMaker(telom_dict['all_intensities'], workbook, main_output_name)
    writer.save()
    logger.info("Done!")


def combgraph_write(comb_dict:dict, directory:str):
    main_output_name = os.path.basename(directory)
    outpath = os.path.join(os.path.dirname(directory), main_output_name + "_combgraph.xlsx")
    logger.debug("Attempting xlsx write to {}.".format(outpath))

    writer = pd.ExcelWriter(outpath, engine='xlsxwriter')
    workbook = writer.book
    workbook.set_properties({'keywords': 'combgraph'})
    for key in comb_dict.keys():
        if key in ['all_intensities']:
            comb_dict[key].to_excel(writer, sheet_name=key, index=False)
        elif key in ['bins']:
            comb_dict[key].to_excel(writer, sheet_name=key)
    combChartMaker(comb_dict['bins'], workbook, main_output_name)
    writer.save()
    logger.info("Done!")


def telomgraph_main():
    parent_dir = user_get_dir()
    xlsx_dirs = get_cell_dirs(parent_dir)
    for directory in xlsx_dirs:
        logger.debug("Running on telomgraph on: {}".format(directory))
        xlsx_files = get_files_in_dir(directory, mode='telomgraph')
        if xlsx_files:
            telom_dict = build_telodf_from_excel(xlsx_files)
            if telom_dict != None:
                telomgraph_write(telom_dict, directory)
            else:
                logger.error("Cannot save empty dataframe.")
        else:
            logger.error("No files to analyze. Skipping directory.")


def combgraph_main():
    parent_dir = user_get_dir()
    xlsx_dirs = get_cell_dirs(parent_dir)
    for directory in xlsx_dirs:
        logger.debug("Running on combgraph on: {}".format(directory))
        xlsx_files = get_files_in_dir(directory, mode='combgraph')
        if xlsx_files:
            comb_dict = build_comb_df_from_excel(xlsx_files)
            if comb_dict != None:
                combgraph_write(comb_dict, directory)
            else:
                logger.error("Cannot save empty dataframe.")
        else:
            logger.error("No files to analyze. Skipping directory.")


if __name__ == "__main__":
    setup_logging()
    root = Tk()
    root.title('Intensity Calculations')
    root.geometry('400x100')
    app = Application(master=root)
    app.mainloop()
    try:
        root.destroy()
    except:
        pass
    # combgraph_main()