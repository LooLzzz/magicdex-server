import os, re, json
from flask import abort, jsonify, make_response
from typing import Union, List
from bson.errors import InvalidId
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from flask_jwt_extended import jwt_required, get_jwt_identity

# from .. import users_db, collections_db
from ..utils import get_arg_dict, get_arg_list, to_json, to_bool, to_amount, CardCondition
from ..models import UserModel, CardModel

collection_parser = RequestParser(bundle_errors=True)
collection_parser.add_argument('cards', location=['form', 'args', 'json'], case_sensitive=False, type=to_json)

get_all_parser = RequestParser(bundle_errors=True)
get_all_parser.add_argument('page',     location=['form', 'args', 'json'], case_sensitive=False, default=1,     type=int)
get_all_parser.add_argument('per_page', location=['form', 'args', 'json'], case_sensitive=False, default=20,    type=int)
# get_all_parser.add_argument('all',      location=['form', 'args', 'json'], case_sensitive=False, default=False, type=to_bool)


card_parser = RequestParser(bundle_errors=True)
card_parser.add_argument('scryfall_id', location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=str)
card_parser.add_argument('amount',      location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_amount)
card_parser.add_argument('tag',         location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_json)
card_parser.add_argument('foil',        location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_bool)
card_parser.add_argument('condition',   location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=CardCondition.parse)
card_parser.add_argument('signed',      location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_bool)
card_parser.add_argument('altered',     location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_bool)
card_parser.add_argument('misprint',    location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_bool)

def data_validator(parser):
    def wrapper(func):
        def decorator(self, card_id:str=None):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)
            
            try:
                if card_id is not None:
                    card = user.collection[card_id] # will throw an exception if card_id is not found
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
                    jsonify({
                        'msg': 'card not found',
                        'errors':e.args 
                    }),
                    404
                ))
            
            if card_id is None:
                return func(self, user=user, **kwargs)
            return func(self, card_id=card_id, user=user, **kwargs)
        return decorator
    return wrapper


class CollectionsApi():
    '''
    A container for the collections api.
    Contains three APIs accesible by inner classes:
        - `CollectionsApi.Collections`
        - `CollectionsApi.All`
        - `CollectionsApi.Cards`
    '''
    class All(Resource):
        '''
        ## `/collections/all` ENDPOINT

        ### GET
        Loads *all* cards associated with a given user from the database.
        
        ### DELETE
        Clears all cards associated with a given user from the database.
        '''
        @jwt_required()
        def get(cls):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)

            data = user.collection \
                    .load_all() \
                    .to_JSON(cards_drop_cols=['user_id'])
            return {
                'total_documents': data['doc_count'],
                'data': data['cards']
            }
        
        @jwt_required()
        def delete(cls):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)

            return user.collection \
                    .clear() \
                    .save()

    class Collections(Resource):
        '''
        ## `/collections` ENDPOINT

        ### GET
        Loads cards associated with a given user from the database.  
        Supports pagination.

        ### DELETE
        Deletes selected `card_id`s associated with a given user from the database.

        ### POST / PUT
        Updates/Inserts cards from given user's collections in the database.
        '''

        @jwt_required()
        def get(self):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)
            kwargs = get_arg_dict(get_all_parser)
            page, per_page = kwargs.values()

            data = user.collection \
                    .load(**kwargs) \
                    .to_JSON(cards_drop_cols=['user_id'])
            res = {
                **kwargs,
                'data': data['cards']
            }

            if page == 1:
                # show total document count on the first page
                res['total_documents'] = data['doc_count']
            if page * per_page < data['doc_count']:
                # show url for the next page if there are cards left to show
                kwargs['page'] += 1
                args = '&'.join([ f'{k}={repr(v)}' for k,v in kwargs.items() ])
                res['next_page'] = f'{os.environ["APP_URL"]}/collections?{args}'
            
            return res

        @jwt_required()
        @data_validator(collection_parser)
        def delete(self, user:UserModel, cards:List[CardModel]):
            return [ card.delete().save() for card in cards ]

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


    class Cards(Resource):
        '''
        ## `/collections` ENDPOINT

        ### GET
        Loads a specific card using it's `card_id` from the database.

        ### DELETE
        Deletes a specific card using it's `card_id` from the database.

        ### POST
        Updates a specific card using it's `card_id` from the database.
        '''
        @jwt_required()
        def get(self, card_id:str):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)

            return user \
                    .collection[card_id] \
                    .to_JSON(drop_cols=['user_id'])

        @jwt_required()
        @data_validator(card_parser)
        def post(self, card_id:str, user:UserModel, **kwargs):
            res = user.collection[card_id] \
                    .update(**kwargs) \
                    .save()

            cols = ['_id'] + list(kwargs.keys())
            return { k:v for k,v in user.collection[card_id].to_JSON().items() if k in cols }
        
        @jwt_required()
        def delete(self, card_id:str):
            user_id, username = get_jwt_identity()
            user = UserModel(user_id)
            
            return user \
                    .collection[card_id] \
                    .delete() \
                    .save()
