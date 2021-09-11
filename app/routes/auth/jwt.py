from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

class JwtEndpoint(Resource):
    '''
    ## `/auth/jwt` ENDPOINT

    ### POST/GET
    Login using saved JWT token.
    '''
    @jwt_required()
    def post(self):
        user_id, username = get_jwt_identity()
        return {
            'msg': f'successfuly logged in',
            'username': username
        }
    
    @jwt_required()
    def get(self):
        return self.post()
