
from flask_restful import Resource, reqparse, request
from DB_DIR import mongo as mng
from AddData.sample_adder import add


class filter(Resource):

    def get(self, patient_number):
        parser = reqparse.RequestParser()
        parser.add_argument("tPoint", type=str, help="The timepoint you are looking for")
        args = parser.parse_args()

        tPoint_proper = "+" + args['tPoint'].lstrip()
        print(tPoint_proper)
        try:
            self.filter = mng.get_filter_by_tPoint(patient_number, tPoint_proper)
            try:
                del self.filter['images']
            except KeyError as e:
                print(e)
                pass
        except TypeError as e:
            self.filter = {}
            print(e)
        return self.filter

    def put(self, patient_number):
        parser = reqparse.RequestParser()
        parser.add_argument("date", type=str, help="The date this sample was collected")
        parser.add_argument('fNum', type=str, help="The filter number on the ring.")
        args = parser.parse_args()
        self.patient = add(patient_number, args['fNum'], args['date'])
        return self.patient
