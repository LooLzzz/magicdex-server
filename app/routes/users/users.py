import os
from typing import List
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from .route_utils import data_validator, parsers
from ...models import UserModel


class UsersEndpoint(Resource):
    '''
    ## `users/` ENDPOINT

    ### GET
    Get user's information.
    
    ### POST
    Update user's information.
    '''

    @jwt_required(optional=True)
    @data_validator(parsers.user_parser)
    def get(self, user:UserModel, **kwargs):
        user_id, identity_username = get_jwt_identity() or (None, None)
        if str(user.user_id) != str(user_id):
            return { 'message': 'you are not authorized to access this resource' }, 401
        
        return user \
                .to_JSON(include_collection=False, drop_cols=['password'])

    @jwt_required()
    @data_validator(parsers.user_parser, data_mandatory=True)
    def post(self, user:UserModel, **kwargs):
        user_id, identity_username = get_jwt_identity() or (None, None)
        if str(user.user_id) != str(user_id):
            return { 'message': 'you are not authorized to access this resource' }, 401

        return user \
                .update(**kwargs)
