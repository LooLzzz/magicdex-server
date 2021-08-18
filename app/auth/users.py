import re
from datetime import datetime
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import create_access_token

from .. import mongo, bcrypt
from ..utils import get_arg_list


users_db = mongo.db['users']
collections_db = mongo.db['collections']

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True)


class UsersApi(Resource):
    def get(self):
        '''login endpoint'''
        username, password = get_arg_list(parser)
        user = users_db.find_one({ 'username': re.compile(username, re.IGNORECASE) })

        if user:
            user_id = user['_id']
            password_hash = user['password']
            if bcrypt.check_password_hash(password_hash, password):
                return { 
                    'msg': 'logged in',
                    'access-token': create_access_token(identity=(str(user_id), username))
                }
            
        return (
            { 'msg': 'username/password combination not found' },
            401
        )

    def post(self):       
        '''register endpoint'''       
        username, password = get_arg_list(parser)
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
                'access-token': create_access_token(identity=(str(user_id), username))
            },
            201
        )
