import os
from typing import Union, List
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from .route_utils import data_validator, parsers
from ...utils import get_arg_list, DatabaseOperation
from ...models import UserModel, CardModel


class CollectionsEndpoint(Resource):
    '''
    ## `/collections` ENDPOINT

    ### GET
    Loads cards associated with a given user from the database.  
    Supports pagination.

    ### DELETE
    Deletes selected `card_id`s associated with a given user from the database.

    ### POST
    Updates or inserts cards from given user's collections in the database.
    '''

    @jwt_required()
    @data_validator(parsers.cardlist_parser)
    def get(self, user:UserModel, cards:List[CardModel]):
        page, per_page = get_arg_list(parsers.pagination_parser)

        data = user.collection \
                .load(page, per_page, cards) \
                .to_JSON(cards_drop_cols=['user_id'])
        res = {
            'page': page,
            'per_page': per_page,
            'data': data['cards']
        }

        if page == 1:
            # show total document count on the first page
            res['total_documents'] = data['doc_count']
        if page * per_page < data['doc_count']:
            # show url for the next page if there are cards left to show
            page += 1
            args = '&'.join([ f'{k}={repr(v)}' for k,v in (page, per_page) ])
            res['next_page'] = f'{os.environ["APP_URL"]}/collections?{args}'
        
        return res

    @jwt_required()
    @data_validator(parsers.cardlist_parser)
    def delete(self, user:UserModel, cards:List[CardModel]):
        cards = [ card.delete() for card in cards ]
        return user.collection \
                .update(cards) \
                .save()

    @jwt_required()
    @data_validator(parsers.cardlist_parser)
    def post(self, user:UserModel, cards:List[CardModel]):
        res = user.collection \
                .update(cards) \
                .save()
        
        # only return fields that were updated
        for card, res_item in zip(cards, res):
            if res_item['action'] == DatabaseOperation.UPDATE:
                fields = list(card.to_dict(drop_cols=['user_id', 'operation'], drop_none=True).keys())
                res_item['card'] = { k:v for k,v in res_item['card'].items() if k in fields }
        return res
