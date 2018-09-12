
from flask_restful import Resource, reqparse, request
from DB_DIR import mongo as mng
from AddData.sample_adder import add


class filter(Resource):

    def get(self, patient_number, filter_number):
        try:
            self.filter = mng.get_filter_by_number(patient_number, filter_number)
            del self.filter['images']
        except TypeError:
            self.filter = {}
        return self.filter

    def put(self, patient_number, filter_number):
        parser = reqparse.RequestParser()
        parser.add_argument("date", type=str, help="The date this sample was collected")
        args = parser.parse_args()
        self.patient = add(patient_number, filter_number, args['date'])
        return self.patient
