from MongoInterface import mongo as mng
from ScrapeTeloView import chart_maker as chm
import logging

logger = logging.getLogger("mainUI.cmMain")

def main():

    patient_list = mng.getPatientList()
    for patientNumber in patient_list:
        patientDoc = mng.retrieveDoc(patientNumber)
        try:
            parameters = [list([item for item in list(patientDoc['filters'].values())][xx].keys()) for xx in
                          range(len(patientDoc['filters']))]
            # remove parameters not in each sample
            result = set(parameters[0])
            for s in parameters[1:]:
                result.intersection_update(s)
            # remove irrelevant parameters
            [result.remove(xx) for xx in ['DateRec', 'images', 'CTCNum', 'tPoint', 'p2qrt', 'p3qrt', 'p4qrt']]
            for parameter in result:
                # make chart using parameter, patNum and parent of current directory
                print(len(patientDoc['filters']))
                try:
                    print("Making chart for %s, patient number: %s" % (parameter, patientNumber))
                    chm.getFigure(patientNumber, parameter, "C:\\Users\\Landon\\ownCloud\\Documents\\Student Work\\Data\\" + patientNumber)
                except FileNotFoundError:
                    print("Couldn't find directory for %s" %  patientNumber)
                    continue
        except IndexError:
            continue


if __name__ == "__main__":
    main()