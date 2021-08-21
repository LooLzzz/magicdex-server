import re, json
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required, get_jwt_identity

from .. import mongo
from ..utils import get_arg_dict, dictkeys_to_lower
from ..models import CardModel, CollectionModel

users_db = mongo.db['users']
collections_db = mongo.db['collections']

parser = RequestParser(bundle_errors=True)
parser.add_argument('cards', location=['form', 'args', 'json'], case_sensitive=False)


class CollectionsApi(Resource):
    '''
    * get - get collection
    * delete - clear collection
    * post - update collection
    '''

    @jwt_required()
    def get(self):
        user_id, username = get_jwt_identity()
        collection = CollectionModel(user_id)

        return collection.to_JSON()

    @jwt_required()
    def delete(self):
        user_id, username = get_jwt_identity()
        collection = CollectionModel(user_id)
        
        res = collection \
                .clear() \
                .save()

        return res

    @jwt_required()
    def post(self):
        user_id, username = get_jwt_identity()
        collection = CollectionModel(user_id)

        args = get_arg_dict(parser)
        cards = json.loads(args['cards'])
        cards = [ CardModel(parent=collection, **dictkeys_to_lower(item)) for item in cards ]
        
        res = collection \
                .update(cards)
                # .save()
        
        # return res.to_JSON()
        return collection.to_JSON()
        # return 200
