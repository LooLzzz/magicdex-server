import re, pytz
from bson.objectid import ObjectId
from datetime import datetime
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import create_access_token

from .. import mongo, bcrypt
from ..utils import get_arg_dict #, get_arg_list

users_db = mongo.db['users']
collections_db = mongo.db['collections']

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True)


class UsersApi(Resource):
    def get(self):
        '''login endpoint'''
        args = get_arg_dict(parser)
        user = users_db.find_one({ 'username': re.compile(args['username'], re.IGNORECASE) })

        if user:
            user_id = user['_id']
            password_hash = user['password']
            if bcrypt.check_password_hash(password_hash, args['password']):
                return {
                    'msg': 'logged in',
                    'access-token': create_access_token(identity=(str(user_id), args['username']))
                }
            
        return (
            {'msg': 'username/password combination not found'},
            401
        )

    def post(self):       
        '''register endpoint'''
        args = get_arg_dict(parser)
        if users_db.find_one({ 'username': re.compile(args['username'], re.IGNORECASE) }):
            return (
                {'msg': 'username already exists'},
                400
            )
        
        user_id = users_db.insert_one({
            'username': args['username'],
            'password': bcrypt.generate_password_hash(args['password']).decode('utf-8'),
            'date': datetime.now()
        }).inserted_id
        
        collections_db.insert_one({
            'user_id': ObjectId(user_id),
            'cards': []
        })

        return (
            {
                'msg': 'user created',
                'access-token': create_access_token(identity=(str(user_id), args['username']))
            },
            201
        )
