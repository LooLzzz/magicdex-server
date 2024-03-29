from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...utils import UserAlreadyExists, UserDoesNotExist
from ...utils import get_arg_dict, to_bool
from ...models import UserModel

parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('username', location=['form', 'args', 'json'], required=True,  nullable=False, case_sensitive=True,  type=str)
parser.add_argument('password', location=['form', 'args', 'json'], required=True,  nullable=False, case_sensitive=True,  type=str)
parser.add_argument('public',   location=['form', 'args', 'json'], required=False, nullable=False, case_sensitive=False, type=to_bool, default=False, store_missing=False)


class UsersEndpoint(Resource):
    '''
    ## `/auth[/users]` ENDPOINT

    ### POST/GET
    Login using a username and password combination **or** a JWT access token.
    
    ### PUT
    Register a new user using a username and password combination.
    '''
    @jwt_required(optional=True)
    def post(self):
        jwt_identity = get_jwt_identity()
        
        if jwt_identity:
            user_id, username = jwt_identity
            return {
                'message': f'successfuly logged in',
                'username': username
            }
        else:
            kwargs = get_arg_dict(parser)
            user = UserModel(username=kwargs['username'])
            try:
                if user.check_password_hash(kwargs['password']):
                    return {
                        'message': f'successfuly logged in',
                        'username': user.username,
                        'access-token': user.create_access_token() # will raise an exception if the user does not exist
                    }
                else:
                    raise UserDoesNotExist
            except UserDoesNotExist as e:
                return (
                    { 'message': 'username and password combination not found' },
                    401
                )

    @jwt_required(optional=True)
    def get(self):
        return self.post()
       
    def put(self):
        kwargs = get_arg_dict(parser)
        user = UserModel(**kwargs)
        
        try:
            user = user.create(kwargs['password'])
            return (
                {
                    'message': 'user created',
                    'username': kwargs['username'],
                    'access-token': user.create_access_token()
                },
                201
            )
        except UserAlreadyExists as e:
            return (
                {
                    'message': 'username already exists',
                    'username': kwargs['username'],
                },
                400
            )
