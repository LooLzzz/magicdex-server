from flask import redirect

from . import app, api
from .routes import auth, collections, users


@app.route('/', defaults={'path': ''})
@app.route('/<string:path>')
def index(path):
    '''
    Catch-all route
    '''
    return {'message': 'this is not the api you are looking for'}, 418


def init_auth_route():
    api.add_resource(auth.UsersEndpoint, '/auth', endpoint='auth')
    api.add_resource(auth.UsersEndpoint, '/auth/users')


def init_phash_route():
    func = lambda: redirect('https://github.com/LooLzzz/magicdex-server/raw/phash/image_data.pickle', 308)
    app.add_url_rule('/phash', 'phash', func, methods=['GET'])


def init_collections_route():
    api.add_resource(collections.CollectionsEndpoint, '/collections', endpoint='collections')
    api.add_resource(collections.CardEndpoint,        '/collections/<string:card_id>', endpoint='collections_card')
    api.add_resource(collections.AllEndpoint,         '/collections/all', endpoint='collections_all')
    
    
def init_users_route():
    api.add_resource(users.UsersEndpoint,       '/users', '/users/<string:username>', endpoint='users')
    api.add_resource(users.CollectionsEndpoint, '/users/<string:username>/collection', endpoint='user_collection')
    api.add_resource(users.CardEndpoint,        '/users/<string:username>/collection/<string:card_id>', endpoint='user_collection_card')
    api.add_resource(users.AllEndpoint,         '/users/<string:username>/collection/all', endpoint='user_collections_all')


## main ##
init_auth_route()
init_phash_route()
init_collections_route()
init_users_route()
