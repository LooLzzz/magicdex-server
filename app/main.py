from . import app, api
from .AuthApi import AuthApi


@app.route('/')
def index():
    return '<h1>Hello from Flask</h1>'


api.add_resource(AuthApi, '/auth')
