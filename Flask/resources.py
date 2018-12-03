from flask.json import jsonify
from flask_restful import Resource, reqparse
from DB_DIR import mongo as mng
from AddData.sample_adder import add
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt)
from Classes.models import User
import json


class logon(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", required=True, type=str, help="Your email address")
        parser.add_argument("password", required=True, type=str, help="Your password")
        args = parser.parse_args()

        current_user = User.find_by_email(args['email'])
        if not current_user:
            return {'message': 'User with email {} doesn\'t exist'.format(args['email'])}
        if current_user.check_password(args['password']):
            access_token = create_access_token(identity=args['email'])
            refresh_token = create_refresh_token(identity=args['email'])
            return {
                'message': 'Logged in as {}'.format(current_user.name),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'message': 'Wrong credentials'}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        return {'access_token': access_token}


class filter(Resource):
    @jwt_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("patient", type=str, help="The patient you are looking for")
        parser.add_argument("tPoint", type=str, help="The timepoint you are looking for")
        args = parser.parse_args()
        tPoint_proper = "+" + args['tPoint'].lstrip()
        try:
            self.filter = mng.get_filter_by_tPoint(args['patient'], tPoint_proper)
            try:
                del self.filter['images']
            except KeyError as e:
                pass
        except TypeError as e:
            self.filter = {'error':'filter not found'}
        return self.filter

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("patient", type=str, help="The patient you are looking for")
        parser.add_argument("date", type=str, help="The date this sample was collected")
        parser.add_argument('fNum', type=str, help="The filter number on the ring.")
        parser.add_argument('mL', type=int, help="How much blood was received for the sample.")
        parser.add_argument('ins', type=str, help="The institute the sample was received from.")
        args = parser.parse_args()
        self.patient = add(args['patient'], args['fNum'], args['date'], args['mL'], args['ins'])
        return self.patient

class All_Patients(Resource):
    def get(self):
        #d = {"#" + str(mng.retrieveDoc(patient)['patient_num']).zfill(3) + " " + patient: mng.retrieveDoc(patient) for patient in mng.getPatientList()}
        d = mng.retrieveAll()
        return jsonify(d)

class Janine_DidNot(Resource):
    def get(self):
        d = mng.getAllNotJanine()
        return jsonify({'Not_Done' : d})