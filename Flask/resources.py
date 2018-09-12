
from flask import request
from flask_restful import Resource, reqparse

from Classes import namer
from Classes.patientizer import Patient
from Classes.filterizer import Filter
from MongoInterface import mongo as mng
from AddData.sample_adder import add


class filter(Resource):

    def get(self, patient_number, filter_number):
        self.filter = mng.get_filter_by_number(patient_number, filter_number)
        return self.filter

    def put(self, patient_number, filter_number):
        date_rec = request.form['data']
        self.patient = add(patient_number, filter_number, date_rec)
        print(self.patient)
        return self.patient