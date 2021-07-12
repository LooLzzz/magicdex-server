import re
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import create_access_token

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


class LoginApi(Resource):
    def get(self):
        username, password = get_arg_list()
        user = db.find_one({ 'username': re.compile(username, re.IGNORECASE) })

        if user:
            password_hash = user['password']
            if bcrypt.check_password_hash(password_hash, password):
                token = create_access_token(identity=username)
                return { 'access-token': token }
            
        return (
            { 'msg': 'username/password combination not found' },
            401
        )
