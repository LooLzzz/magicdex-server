from flask import abort, jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful.reqparse import RequestParser
from bson.errors import InvalidId

from ...utils import get_arg_dict, to_json, to_bool, to_amount, to_card_list
from ...utils import CardCondition
from ...models import UserModel, CardModel


def data_validator(parser):
    '''
    Validates the data sent by the user.
    
    The decorated method should have one of the following signatures:
    - `(self, user:UserModel, **kwargs)`
    - `(self, user:UserModel, card_id:str, **kwargs)`

    :param parser: The parser object to validate for.
    '''
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
                if 'cards' in kwargs and kwargs['cards']:
                    kwargs['cards'] = [ CardModel(parent=user.collection, **item) for item in kwargs['cards'] ]
            except ValueError as e:
                abort(make_response(
                    jsonify({
                        'msg': 'bad card request',
                        'errors': e.args
                    }),
                    400
                ))
            except (InvalidId, KeyError) as e:
                abort(make_response(
                    jsonify({
                        'msg': 'card not found',
                        'errors': e.args
                    }),
                    404
                ))
            
            if card_id is None:
                return func(self, user=user, **kwargs)
            return func(self, user=user, card_id=card_id, **kwargs)
        return decorator
    return wrapper


class parsers():
    '''
    Parsers for the collection routes
    '''
    collection_parser = RequestParser(bundle_errors=True)
    collection_parser.add_argument('cards', location=['form', 'args', 'json'], case_sensitive=False, default=[], type=to_card_list)


    get_all_parser = RequestParser(bundle_errors=True)
    get_all_parser.add_argument('page',     location=['form', 'args', 'json'], case_sensitive=False, default=1,  type=int)
    get_all_parser.add_argument('per_page', location=['form', 'args', 'json'], case_sensitive=False, default=20, type=int)
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
