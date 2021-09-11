# from flask import redirect
# from flask_jwt_extended import jwt_required

from . import app, api
from .routes import auth, cards, collections


@app.route('/', defaults={'path': ''})
@app.route('/<string:path>')
def index(path):
    '''
    Catch-all route
    '''
    return {'msg': 'this is not the api you are looking for'}, 418


def init_auth_route():
    api.add_resource(auth.UsersEndpoint, '/auth', endpoint='auth')
    api.add_resource(auth.UsersEndpoint, '/auth/users')
    api.add_resource(auth.JwtEndpoint,   '/auth/jwt')


def init_cards_route():
    api.add_resource(cards.PhashEndpoint, '/cards/phash')
    # api.add_resource(SellersEndpoint,     '/cards/sellers')


def init_collections_route():
    api.add_resource(collections.CollectionsEndpoint, '/collections')
    api.add_resource(collections.CardEndpoint,        '/collections/<string:card_id>')
    api.add_resource(collections.AllEndpoint,         '/collections/all')


## main ##
init_auth_route()
init_cards_route()
init_collections_route()
