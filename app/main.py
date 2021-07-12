from flask_pymongo import ASCENDING

from . import app, api
from .auth import LoginApi, RegisterApi, JwtApi
from .users import UsersApi
from .cards import CardsApi


@app.route('/')
def index():
    return '<h1>Hello from Flask</h1>'


## auth ##
api.add_resource(LoginApi, '/auth/login')
api.add_resource(RegisterApi, '/auth/register')
api.add_resource(JwtApi, '/auth')

## cards ##
api.add_resource(CardsApi, '/cards', '/cards/searchSellers')

## users ##
api.add_resource(UsersApi, '/users/<string:userId>')
