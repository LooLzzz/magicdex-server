import re
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .. import mongo, bcrypt


db = mongo.db['users']

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True)

def get_arg_list():
    args = parser.parse_args()
    username = args['username']
    password = args['password']
    return (username, password)


class RegisterApi(Resource):
    def post(self):
        '''create a new user'''
        #TODO all this shiz
        pass
