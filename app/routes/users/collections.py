import os
from typing import List
from flask_restful import Resource
from flask_jwt_extended import jwt_required

from .route_utils import data_validator, parsers
from ...utils import get_arg_dict
from ...models import UserModel, CardModel


class CollectionsEndpoint(Resource):
    '''
    ## `users/<username>/collections` ENDPOINT

    ### GET, POST
    Loads cards associated with a given user from the database.  
    Supports pagination.
    '''

    @jwt_required(optional=True)
    @data_validator(parsers.cardlist_parser)
    def get(self, user:UserModel, cards:List[CardModel]):
        args = get_arg_dict(parsers.pagination_parser)
        page, per_page = args['page'], args['per_page']
        app_url = os.getenv("APP_URL") or os.getenv("DETA_SPACE_APP_HOSTNAME")

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
            args = '&'.join([ f'{k}={v}' for k,v in args.items() ])
            res['next_page'] = f'{app_url}/collections?{args}'
        
        return res

    @jwt_required(optional=True)
    @data_validator(parsers.cardlist_parser)
    def post(self, user:UserModel, cards:List[CardModel]):
        args = get_arg_dict(parsers.pagination_parser)
        page, per_page = args['page'], args['per_page']

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
            args = '&'.join([ f'{k}={v}' for k,v in args.items() ])
            res['next_page'] = f'{os.getenv("APP_URL")}/collections?{args}'
        
        return res
