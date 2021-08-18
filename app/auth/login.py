import re
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import create_access_token

from .. import mongo, bcrypt
from ..utils import get_arg_list


db = mongo.db['users']

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False, type=str)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True, type=str)


class LoginApi(Resource):
    def get(self):
        username, password = get_arg_list(parser)
        user = db.find_one({ 'username': re.compile(username, re.IGNORECASE) })

        if user:
            user_id = user['_id']
            password_hash = user['password']
            if bcrypt.check_password_hash(password_hash, password):
                token = create_access_token(identity=(str(user_id), username))
                return { 'access-token': token }
            
        return (
            { 'msg': 'username/password combination not found' },
            401
        )
