"""
Contains methods for preprocessing data
"""



def DRE_Closest_Result(word: str):
    from difflib import get_close_matches
    posssible_cases = ['Nodule', 'Induration', 'Benign', 'Asymmetric', 'Unknown', 'Enlarged', 'Normal']
    result = get_close_matches(word, posssible_cases)
    return result

def tScore_Scraper(word: str):
    import re
    base = re.split("(m|n)", word.lower())
    if base[0] == 'u':
        return "Unknown"
    if len(base) > 1:
        base[1] = base[1] + base[2]
        base[2] = base[2] + base[3]
        base = base[:2]
    return base[0].upper()

def Calc_Cores(proc: dict):
    pos_cores = proc['#Positive Cores']
    tot_cores = proc['#Cores']
    if 'nan' not in str(pos_cores) and 'nan' not in str(tot_cores):
        value = str(round((int(pos_cores) / int(tot_cores)), 1)) + " pos"
    else:
        value = 'nan'
    return value

# for grabbing the most recent gleason score from a patient
def Procedures_Grabber(procedures: dict, clinical_para: str):
    import numpy as np
    recent = sorted(list(procedures.keys()))[-1]
    proc = procedures[recent]
    if clinical_para.lower() == "cores":
        value = Calc_Cores(proc)
    else:
        value = str(proc[clinical_para])
    if clinical_para.lower() == 'primary/secondary' and len(value) == 1:
        print("Only one value found for primary/secondary. Doubling up!")
        value = value + value
    if clinical_para.lower() == 'gleason':
        value = value.zfill(2)
    if value.lower() == 'nan':
        value = 'Unknown'
    return value


def TimePointer(point: dict, telo_para: str) -> float:
    import numpy as np
    if len(point.keys()) > 0:
        value = point[list(point.keys())[0]][telo_para]
        if value == 0:
            value = str(np.nan)
        return value
    else:
        return str(np.nan)
