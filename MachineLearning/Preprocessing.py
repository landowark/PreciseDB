"""
Contains methods for preprocessing data
"""

def DRE_Closest_Result(word):
    from difflib import get_close_matches
    posssible_cases = ['Nodule', 'Induration', 'Benign', 'Asymmetric', 'Unknown', 'Enlarged', 'Normal']
    result = get_close_matches(word, posssible_cases)
    return result

