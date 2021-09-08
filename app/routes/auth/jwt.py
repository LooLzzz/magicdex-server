from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

class JwtApi(Resource):
    '''
    ## `/auth/jwt` ENDPOINT

    ### GET
    Login using saved JWT token.
    '''
    @jwt_required()
    def get(self):
        user_id, username = get_jwt_identity()
        return {
            'msg': f'successfuly logged in',
            'username': username
        }
