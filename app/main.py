from flask_jwt_extended import jwt_required

from . import app, api
from .auth import UsersApi, JwtApi
from .cards import CardsApi


@app.route('/')
def index():
    return { 'msg': 'this is not the api you are looking for' }


## auth ##
api.add_resource(UsersApi, '/auth/users', endpoint='AuthApi_Users')
api.add_resource(JwtApi, '/auth/jwt')


## cards ##
api.add_resource(CardsApi, '/cards/sellers')

@app.route('/cards/phash', methods=['GET'])
@jwt_required()
def getInitialPhash():
    pass


## users ##
api.add_resource(UsersApi, '/users/<string:userId>')
