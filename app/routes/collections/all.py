from typing import List
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from .route_utils import data_validator, parsers
from ...models import UserModel, CardModel

class AllEndpoint(Resource):
    '''
    ## `/collections/all` ENDPOINT

    ### GET
    Loads *all* cards associated with a given user from the database.

    ### DELETE
    Clears all cards associated with a given user from the database.
    '''
    @jwt_required()
    @data_validator(parsers.cardlist_parser)
    def get(self, user:UserModel, cards:List[CardModel]):
        user_id, username = get_jwt_identity()
        user = UserModel(user_id)

        data = user.collection \
                .load_all(cards) \
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
