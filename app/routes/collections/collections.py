import os
from typing import Union, List
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from .__utils import data_validator, parsers
from ...utils import get_arg_dict, DatabaseOperation
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
    def get(self):
        user_id, username = get_jwt_identity()
        user = UserModel(user_id)
        kwargs = get_arg_dict(parsers.get_all_parser)
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
    @data_validator(parsers.collection_parser)
    def delete(self, user:UserModel, cards:List[CardModel]):
        return [ card.delete().save() for card in cards ]

    @jwt_required()
    @data_validator(parsers.collection_parser)
    def post(self, user:UserModel, cards:List[CardModel]):
        res = user.collection \
                .update(cards) \
                .save()
        
        # only return fields that were updated
        for card, res_item in zip(cards, res):
            if card.operation == DatabaseOperation.UPDATE:
                fields = list(card.to_dict(drop_cols=['user_id', 'operation'], drop_none=True).keys())
                res_item['card'] = { k:v for k,v in res_item['card'].items() if k in fields }
        return res

    # @jwt_required()
    # @data_validator(parsers.collection_parser)
    # def put(self, user:UserModel, cards:List[CardModel]):
    #     return user.collection \
    #             .update(cards) \
    #             .save()
