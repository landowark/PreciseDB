import datetime

from flask import request
from flask_restful import Resource

from Classes import namer
from Classes.patientizer import Patient
from Classes.filterizer import Filter
from MongoInterface import mongo as mng


class filter(Resource):

    def get(self, patient_number, filter_number):
        self.filter = mng.get_filter_by_number(patient_number, filter_number)
        return self.filter

    def put(self, patient_number, filter_number):
        date_rec = request.form['data']
        self.patient = Patient(namer.parsePatient(patient_number)).jsonable()
        self.filter = Filter(namer.parseFilter(filter_number)).jsonable()
        self.filter['DateRec'] = date_rec
        self.patient['filters'][filter_number] = self.filter
        return self.patient