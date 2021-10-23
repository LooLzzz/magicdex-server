from flask import abort, jsonify, make_response
from flask_jwt_extended import get_jwt_identity
from flask_restful.reqparse import RequestParser
from bson.errors import InvalidId

from ...utils import get_arg_dict, to_taglist, to_bool, to_amount, to_card
from ...utils import CardCondition
from ...models import UserModel, CardModel


def data_validator(parser, data_mandatory=False):
    '''
    Validates the data sent by the user.
    
    The decorated method should have one of the following signature:
    - `(self, user:UserModel, **kwargs)`

    :param parser: The parser object to validate for.
    :param data_mandatory: If `True`, data received from the request must **not** be empty. Defaults to `False`.
    '''
    def outer(func):
        def inner(self, username:str=None, card_id:str=None):
            user_id, identity_username = get_jwt_identity() or (None, None)
            
            try:
                if username:
                    user = UserModel(username=username)
                    if not user:
                        abort(make_response(
                            jsonify({
                                'message': 'user does not exist',
                            }), 404
                        ))
                    if str(user.user_id) != str(user_id) and not user.public:
                        abort(make_response(
                            jsonify({
                                'message': 'you are not authorized to access this resource',
                            }), 401
                        ))
                else:
                    user = UserModel(user_id=user_id)
            
                kwargs = get_arg_dict(parser)
                if card_id is not None:
                    user.collection[card_id] # will load the card and throw an exception if card_id is not found
                    kwargs['card_id'] = card_id
                if kwargs and 'cards' in kwargs and kwargs['cards']: # all the checks!
                    kwargs['cards'] = [ CardModel(parent=user.collection, **item) for item in kwargs['cards'] ]
                elif data_mandatory and not kwargs:
                    abort(make_response(
                        jsonify({ 'message': 'no data provided' }),
                        400
                    ))
            except ValueError as e:
                abort(make_response(
                    jsonify({
                        'message': 'bad card request',
                        'errors': e.args
                    }), 400
                ))
            except (InvalidId, KeyError) as e:
                abort(make_response(
                    jsonify({
                        'message': 'card not found',
                        'errors': e.args
                    }), 404
                ))
            
            return func(self, user=user, **kwargs)
        return inner
    return outer


class parsers():
    '''
    Parsers for the collection routes
    '''
    user_parser = RequestParser(bundle_errors=True, trim=True)
    user_parser.add_argument('username', location=['form', 'args', 'json'], case_sensitive=True,  store_missing=False, type=str)
    user_parser.add_argument('password', location=['form', 'args', 'json'], case_sensitive=True,  store_missing=False, type=str)
    user_parser.add_argument('public',   location=['form', 'args', 'json'], case_sensitive=False, store_missing=False, type=to_bool)
    
    
    cardlist_parser = RequestParser(bundle_errors=True, trim=True)
    cardlist_parser.add_argument('cards', location=['json'], case_sensitive=False, default=[], type=to_card, action='append')


    pagination_parser = RequestParser(bundle_errors=True, trim=True)
    pagination_parser.add_argument('page',     location=['form', 'args'], case_sensitive=False, default=1,  type=int)
    pagination_parser.add_argument('per_page', location=['form', 'args'], case_sensitive=False, default=20, type=int)
    
    
    card_parser = RequestParser(bundle_errors=True, trim=True)
    card_parser.add_argument('scryfall_id', location=['json', 'args'], case_sensitive=False, store_missing=False, type=str)
    card_parser.add_argument('amount',      location=['json', 'args'], case_sensitive=False, store_missing=False, type=to_amount)
    card_parser.add_argument('tag',         location=['args'],         case_sensitive=False, store_missing=False, type=to_taglist)
    card_parser.add_argument('tag',         location=['json'],         case_sensitive=False, store_missing=False, type=str, action='append')
    card_parser.add_argument('foil',        location=['json', 'args'], case_sensitive=False, store_missing=False, type=to_bool)
    card_parser.add_argument('condition',   location=['json', 'args'], case_sensitive=False, store_missing=False, type=CardCondition.parse)
    card_parser.add_argument('signed',      location=['json', 'args'], case_sensitive=False, store_missing=False, type=to_bool)
    card_parser.add_argument('altered',     location=['json', 'args'], case_sensitive=False, store_missing=False, type=to_bool)
    card_parser.add_argument('misprint',    location=['json', 'args'], case_sensitive=False, store_missing=False, type=to_bool)
