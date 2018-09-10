from flask_restful import Resource
from MongoInterface import mongo as mng

class filter(Resource):
    def get(self, patient_number, filter_number):
        self.filter = mng.get_filter_by_number(patient_number, filter_number)
        return self.filter
