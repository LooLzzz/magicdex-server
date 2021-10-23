from typing import List
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from .route_utils import data_validator, parsers
from ...models import UserModel, CardModel

class AllEndpoint(Resource):
    '''
    ## `users/<username>/collections/all` ENDPOINT

    ### GET, POST
    Loads *all* cards associated with a given user from the database.
    '''
    @jwt_required(optional=True)
    @data_validator(parsers.cardlist_parser)
    def get(self, user:UserModel, cards:List[CardModel]):
        data = user.collection \
                .load_all(cards) \
                .to_JSON(cards_drop_cols=['user_id'])
        return {
            'total_documents': data['doc_count'],
            'data': data['cards']
        }
    
    @jwt_required(optional=True)
    @data_validator(parsers.cardlist_parser)
    def post(self, user:UserModel, cards:List[CardModel]):
        data = user.collection \
                .load_all(cards) \
                .to_JSON(cards_drop_cols=['user_id'])
        return {
            'total_documents': data['doc_count'],
            'data': data['cards']
        }
