from flask import redirect
from flask_jwt_extended import jwt_required

from . import app, api
from .routes import AuthUsersApi, JwtApi, CollectionsApi, CardsApi


@app.route('/')
def index():
    return {'msg': 'this is not the api you are looking for'}, 418

# @jwt_required()
@app.route('/cards/phash', methods=['GET'])
def getInitialPhash():
    return redirect('https://github.com/LooLzzz/magicdex-server/raw/phash/border_crop.pickle', 303)


def start_auth_endpoint():
    api.add_resource(AuthUsersApi, '/auth/users', '/auth/users/', endpoint='AuthUsersApi')
    api.add_resource(JwtApi, '/auth/jwt', '/auth/jwt/')

def start_cards_endpoint():
    api.add_resource(CardsApi, '/cards/sellers', '/cards/sellers/')

def start_collections_endpoint():
    # api.add_resource(UsersApi, '/collections/<string:user_id>')
    api.add_resource(CollectionsApi.Collection, '/collections', '/collections/')
    api.add_resource(CollectionsApi.Card, '/collections/<string:card_id>', '/collections/<string:card_id>/')


## main
start_auth_endpoint()
start_cards_endpoint()
start_collections_endpoint()
