from flask import redirect
from flask_jwt_extended import jwt_required

from . import app, api
from .auth import UsersApi as AuthUsersApi, JwtApi
from .users import UsersApi
from .cards import CardsApi


@app.route('/')
def index():
    return {'msg': 'this is not the api you are looking for'}, 418

# @jwt_required()
@app.route('/cards/phash', methods=['GET'])
def getInitialPhash():
    return redirect('https://github.com/LooLzzz/magicdex-server/raw/phash/border_crop.pickle', 303)


def start_auth_endpoint():
    api.add_resource(AuthUsersApi, '/auth/users', endpoint='AuthUsersApi')
    api.add_resource(JwtApi, '/auth/jwt')

def start_cards_endpoint():
    api.add_resource(CardsApi, '/cards/sellers')

def start_users_endpoint():
    # api.add_resource(UsersApi, '/users/<string:user_id>')
    api.add_resource(UsersApi, '/users')


## main
start_auth_endpoint()
start_cards_endpoint()
start_users_endpoint() # change this route to `/collections` maybe?
