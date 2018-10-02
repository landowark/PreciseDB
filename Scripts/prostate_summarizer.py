
import pymongo as mng
import json


db = mng.MongoClient().prostate_actual.patient
patient_list = [doc['_id'] for doc in db.find().batch_size(10)]

patients = {}

for patientNum in patient_list:
	doc = db.find_one({'_id' : patientNum}, { "_id" : 0 })
	for x in doc['filters'].keys():
		del doc['filters'][x]['images']
	patients[patientNum] = doc
	
with open('C:\\Users\\Landon\\Downloads\\Prostate_Abridged.json', 'w') as fp:
    json.dump(patients, fp, sort_keys=True, indent=4)