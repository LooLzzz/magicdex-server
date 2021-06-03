from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from . import mongo, bcrypt


db = mongo.db['users']

parser = RequestParser()
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)

def get_arg_list(self):
    args = parser.parse_args()
    username = args['username']
    password = args['password']
    return (username, password)


class AuthApi(Resource):
    def get(self):
        # TODO return JWT or some sort of auth token
        username, password = get_arg_list()

        user = db.find_one({'username': username})
        
        if user:
            password_hash = user['password']
            if bcrypt.check_password_hash(password_hash, password):
                return (
                    {
                        'message': 'logged in',
                        'auth_token': 'TODO',
                    }, 200
                )
            
        return (
            {
                'message': 'username & password combination not found',
            }, 401
        )


    def post(self):
        return self.get()
