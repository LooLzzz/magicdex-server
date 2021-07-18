import re
from datetime import datetime
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import create_access_token

from .. import mongo, bcrypt


users_db = mongo.db['users']
collections_db = mongo.db['collections']

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True)

def get_arg_list():
    args = parser.parse_args()
    username = args['username']
    password = args['password']
    return (username, password)


class UsersApi(Resource):
    def get(self):
        '''login endpoint'''
        username, password = get_arg_list()
        user = users_db.find_one({ 'username': re.compile(username, re.IGNORECASE) })

        if user:
            password_hash = user['password']
            if bcrypt.check_password_hash(password_hash, password):
                return { 
                    'msg': 'logged in',
                    'access-token': create_access_token(identity=username)
                }
            
        return (
            { 'msg': 'username/password combination not found' },
            401
        )

    def post(self):       
        '''register endpoint'''       
        username, password = get_arg_list()
        if users_db.find_one({ 'username': re.compile(username, re.IGNORECASE) }):
            return (
                { 'msg': 'username already taken' },
                400
            )
        
        user_id = users_db.insert_one({
            'username': username,
            'password': bcrypt.generate_password_hash(password),
            'date': datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%S.000Z")
        })
        collections_db.insert_one({
            'userid': user_id,
            'cards': []
        })
        return (
            { 
                'msg': 'user created',
                'access-token': create_access_token(identity=username)
            },
            201
        )
