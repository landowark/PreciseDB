import zipfile
import os
import tempfile
from AddData import telo_scraper
import shutil


def extract_files(zip_file, patient_number, filter_number):
    zf = zipfile.ZipFile(zip_file, 'r')
    temp = os.path.join(tempfile.gettempdir(), patient_number, filter_number)
    zf.extractall(path=temp)
    telo_scraper.scrape_dir(temp)
    shutil.rmtree(temp)
