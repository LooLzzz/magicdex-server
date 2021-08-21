from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import create_access_token

from ...utils import get_arg_dict #, get_arg_list
from ...models import UserModel

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True)


class AuthUsersApi(Resource):
    def get(self):
        '''login endpoint'''
        args = get_arg_dict(parser)
        user = UserModel(username=args['username'])

        if user and user.check_password_hash(args['password']):
            return {
                'msg': f'successfuly logged in as {args["username"]}',
                'access-token': user.create_access_token()
            }
        else:
            return (
                { 'msg': 'username and password combination not found' },
                401
            )
            
    def post(self):
        self.put()
    
    def put(self):
        '''register endpoint'''
        args = get_arg_dict(parser)
        if UserModel.exists(username=args['username']):
            return (
                {
                    'msg': 'username already exists',
                    'username': args['username'],
                },
                400
            )
        
        user = UserModel.create(args['username'], args['password'])
        return (
            {
                'msg': 'user created',
                'access-token': create_access_token(identity=(str(user.user_id), args['username']))
            },
            201
        )
