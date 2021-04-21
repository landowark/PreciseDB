# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 11:02:59 2015

This Modules contains input/output functions for reading/writing files.

@author: Landon
"""

import sys

## INPUT MENUS##

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
        
def excel_write(path, data_out):
    import pandas as pd
    writer = pd.ExcelWriter(path + 'data_dump.xlsx')
    print("Writing to Excel file...", path + 'data_dump.xlsx')
    data_out.to_excel(writer)
    writer.save()
    
def output_parent(path):
    import os
    path = os.path.dirname(path)
    return(path)
    
def write_table(table, title, path, file_name):
    import os
    table_txt = table.get_string()
    with open(os.path.join(path, file_name), 'a') as file:
        file.write('\n' + title + '\n')
        file.write(table_txt)
    file.close()