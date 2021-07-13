from . import app, api
from .auth import UsersApi, JwtApi
from .cards import CardsApi


@app.route('/')
def index():
    return '<h1>Hello from Flask</h1>'


## auth ##
api.add_resource(UsersApi, '/auth/users', endpoint='AuthApi_Users')
api.add_resource(JwtApi, '/auth/jwt')

## cards ##
api.add_resource(CardsApi, '/cards', '/cards/sellers')

## users ##
api.add_resource(UsersApi, '/users/<string:userId>')
