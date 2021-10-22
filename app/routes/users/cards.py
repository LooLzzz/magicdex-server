from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...models import UserModel


class CardEndpoint(Resource):
    '''
    ## `users/<username>/collections/<card_id>` ENDPOINT

    ### GET, POST
    Loads a specific card using it's `card_id` from the database.
    '''
    @jwt_required(optional=True)
    def get(self, card_id:str, username:str=None):
        user_id, identity_username = get_jwt_identity() or (None, None)
        if username:
            user = UserModel(username=username)
            if not user:
                return {'message': 'user does not exist'}, 404
            if username != identity_username and not user.public:
                return {'message': 'you are not authorized to access this resource'}, 401
        else:
            user = UserModel(user_id=user_id)
        
        return user \
                .collection[card_id] \
                .to_JSON(drop_cols=['user_id'])
    
    @jwt_required(optional=True)
    def post(self, card_id:str, username:str=None):
        user_id, identity_username = get_jwt_identity() or (None, None)
        if username:
            user = UserModel(username=username)
            if username != identity_username and not user.public:
                return {'message': 'you are not authorized to access this resource'}, 401
        else:
            user = UserModel(user_id=user_id)
        
        return user \
                .collection[card_id] \
                .to_JSON(drop_cols=['user_id'])
