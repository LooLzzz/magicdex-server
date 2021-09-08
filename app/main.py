from flask import redirect
# from flask_jwt_extended import jwt_required

from . import app, api
from .routes import AuthUsersApi, JwtApi, CollectionsApi, SellersApi


@app.route('/', defaults={'path': ''})
@app.route('/<string:path>')
def index(path):
    return {'msg': 'this is not the api you are looking for'}, 418


def start_auth_endpoint():
    api.add_resource(AuthUsersApi, '/auth/users')
    api.add_resource(JwtApi, '/auth/jwt')


def start_cards_endpoint():
    api.add_resource(SellersApi, '/cards/sellers')
    app.add_url_rule('/cards/phash', methods=['GET'], endpoint='phash', view_func=lambda: redirect('https://github.com/LooLzzz/magicdex-server/raw/phash/border_crop.pickle', 308))


def start_collections_endpoint():
    api.add_resource(CollectionsApi.Collections, '/collections')
    api.add_resource(CollectionsApi.Cards,       '/collections/<string:card_id>')
    api.add_resource(CollectionsApi.All,         '/collections/all')


## main ##
start_auth_endpoint()
start_cards_endpoint()
start_collections_endpoint()
