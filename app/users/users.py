import re
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .. import mongo


class UsersApi(Resource):
    '''
    getUserCollection()     - get - get collection

    clearUserCollection()   - delete - clear collection
    
    updateUserCollection()  - post - update collection
    '''
    pass
