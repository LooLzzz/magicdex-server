from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...models import UserModel


class AllEndpoint(Resource):
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
