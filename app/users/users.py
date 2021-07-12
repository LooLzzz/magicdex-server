import re
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import mongo


class UsersApi(Resource):
    '''
    getUserCollection()     - get - get collection

    clearUserCollection()   - delete - clear collection
    
    updateUserCollection()  - post - update collection
    '''
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        print(current_user)

    @jwt_required()
    def delete(self):
        pass

    @jwt_required()
    def post(self):
        pass
