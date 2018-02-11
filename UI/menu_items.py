# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 11:02:59 2015

This Modules contains input/output functions for reading/writing files.

@author: Landon
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QAction, QFileDialog, QApplication, QProgressBar)

## INPUT MENUS##

def getFile():
    app = QApplication(sys.argv)
    src_file = QFileDialog.getOpenFileName(None, 'Open working directory', "P:\\Quon Prostate")[0]
    return src_file

def getDir():
    app = QApplication(sys.argv)
    src_dir = QFileDialog.getExistingDirectory(None, 'Open working directory', "P:\\Quon Prostate", QFileDialog.ShowDirsOnly)
    return src_dir

def recur_find(path, f_type): #finds all files of type(f_type) in directory tree.
    import fnmatch
    import os
    matches = []
    for root, dirnames, filenames in os.walk(path):
      for filename in fnmatch.filter(filenames, '*.' + f_type):
        matches.append(os.path.join(root, filename))
    return(matches)
    
def file_finder(path, f_type):
    import glob
    return(glob.glob(path + '/*.' + f_type))
    
## OUTPUT MENUS##
    
def make_dir(obtain):
    import os
    if not os.path.exists(os.path.dirname(obtain)):
        os.makedirs(os.path.dirname(obtain))
        
def excel_write(data_out):
    import pandas as pd
    app = QApplication(sys.argv)
    path = getDir() + '/'
    writer = pd.ExcelWriter(path + 'data_dump.xlsx')
    print("Writing to Excel file...", path + 'data_dump.xlsx')
    data_out.to_excel(writer)
    writer.save()
    
def output_parent(path):
    import os
    path = os.path.split(path)
    return(path)
    
def write_table(table, title, path, file_name):
    path = path + '/'
    table_txt = table.get_string()
    with open(path + file_name, 'a') as file:
        file.write('\n' + title + '\n')
        file.write(table_txt)
        
## MISC. MENU ITEMS ##

def yes_no(titl = "Yes or No", tex = "What do you want"):
    import tkinter
    frame = tkinter.Tk()
    frame.withdraw()
    from tkinter import messagebox
    result = messagebox.askyesno(titl, tex, icon='warning')
    return result