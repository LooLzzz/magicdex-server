import re, json
from flask import abort, jsonify, make_response
from typing import Union, List
from bson import ObjectId
from bson.errors import InvalidId
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required, get_jwt_identity

# from .. import users_db, collections_db
from ..utils import get_arg_dict
from ..models import UserModel, CardModel

collection_parser = RequestParser(bundle_errors=True)
collection_parser.add_argument('cards', location=['form', 'args', 'json'], case_sensitive=False)

card_parser = RequestParser(bundle_errors=True)
card_parser.add_argument('scryfall_id', location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('amount',      location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('tag',         location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('foil',        location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('condition',   location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('signed',      location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('altered',     location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)
card_parser.add_argument('misprint',    location=['form', 'args', 'json'], case_sensitive=False, store_missing=False)


def data_validator(parser):
    def wrapper(func):
        def decorator(self, card_id:str=None):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)
            
            try:
                if card_id is not None:
                    card = user.collection[card_id]
                kwargs = get_arg_dict(parser)
                if not kwargs:
                    abort(make_response(
                        jsonify({ 'msg': 'no data provided' }),
                        400
                    ))
                if 'cards' in kwargs:
                    kwargs['cards'] = [ CardModel(parent=user.collection, **item) for item in kwargs['cards'] ]
            except (InvalidId, KeyError) as e:
                abort(make_response(
                    jsonify({ 'msg':'card not found', 'errors':e.args }),
                    404
                ))
            
            if card_id is None:
                return func(self, user=user, **kwargs)
            return func(self, card_id=card_id, user=user, **kwargs)
        return decorator
    return wrapper


class CollectionsApi():
    class Collection(Resource):
        '''
        * get - get collection
        * delete - clear collection
        * put/post - update collection
        '''

        @jwt_required()
        def get(self):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)

            return user.collection \
                    .load_all() \
                    .to_JSON()

        @jwt_required()
        def delete(self):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)
            
            return user.collection \
                    .clear() \
                    .save()

        @jwt_required()
        @data_validator(collection_parser)
        def put(self, user:UserModel, cards:List[CardModel]):
            return user.collection \
                    .update(cards) \
                    .save()

        @jwt_required()
        @data_validator(collection_parser)
        def post(self, user:UserModel, cards:List[CardModel]):
            return user.collection \
                    .update(cards) \
                    .save()


    class Card(Resource):
        @jwt_required()
        def get(self, card_id:str):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)

            return user \
                    .collection[card_id] \
                    .to_JSON()

        @jwt_required()
        @data_validator(card_parser)
        def post(self, card_id:str, user:UserModel, **kwargs):
            res = user.collection[card_id] \
                    .update(**kwargs) \
                    .save()

            cols = ['_id'] + list(kwargs)
            return { k:v for k,v in user.collection[card_id].to_JSON().items() if k in cols }
        
        @jwt_required()
        def delete(self, card_id:str):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)
            
            card = user.collection[card_id]
            card.amount = -1
            return card.save()
