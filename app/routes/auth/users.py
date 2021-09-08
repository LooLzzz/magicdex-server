from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from ...utils import UserAlreadyExists, UserDoesNotExist, get_arg_dict #, get_arg_list
from ...models import UserModel

parser = RequestParser(bundle_errors=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=False, type=str)
parser.add_argument('password', location=['form', 'args', 'json'], required=True, nullable=False, case_sensitive=True, type=str)


class AuthUsersApi(Resource):
    '''
    ## `/auth/jwt` ENDPOINT

    ### GET
    Login using a username and password combination.
    
    ### PUT
    Register a new user a username and password combination.
    '''
    def get(self):
        kwargs = get_arg_dict(parser)
        user = UserModel(username=kwargs['username'])

        try:
            if user.check_password_hash(kwargs['password']):
                return {
                    'msg': f'successfuly logged in',
                    'username': kwargs['username'],
                    'access-token': user.create_access_token() # will raise an exception if the user does not exist
                }
            else:
                raise UserDoesNotExist
        except UserDoesNotExist as e:
            return (
                { 'msg': 'username and password combination not found' },
                401
            )
       
    def put(self):
        kwargs = get_arg_dict(parser)
        user = UserModel(username=kwargs['username'])
        
        try:
            user = user.create(kwargs['password'])
            return (
                {
                    'msg': 'user created',
                    'username': kwargs['username'],
                    'access-token': user.create_access_token()
                },
                201
            )
        except UserAlreadyExists as e:
            return (
                {
                    'msg': 'username already exists',
                    'username': kwargs['username'],
                },
                400
            )
