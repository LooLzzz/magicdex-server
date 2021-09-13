from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from .route_utils import data_validator, parsers
from ...models import UserModel


class CardEndpoint(Resource):
    '''
    ## `/collections/<card_id>` ENDPOINT

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
    @data_validator(parsers.card_parser)
    def post(self, card_id:str, user:UserModel, **kwargs):
        res = user.collection[card_id] \
                .update(**kwargs) \
                .save()

        fields = {'_id', 'scryfall_id'} | set(kwargs.keys())
        return { k:v for k,v in user.collection[card_id].to_JSON().items() if k in fields }
    
    @jwt_required()
    def delete(self, card_id:str):
        user_id, username = get_jwt_identity()
        user = UserModel(user_id)
        
        return user \
                .collection[card_id] \
                .delete() \
                .save()
