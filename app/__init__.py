import os, certifi
from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_restful import Api
from flask_sslify import SSLify


## init flask app ##
app = Flask(__name__)

## config stuff ##
app.url_map.strict_slashes = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_RW_URI')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(weeks=4)

## addons ##
sslify = SSLify(app)
mongo = PyMongo(app, tlsCAFile=certifi.where())
bcrypt = Bcrypt(app)
api = Api(app)
jwt = JWTManager(app)
cors = CORS(app)

## mongodb collections ##
users_db = mongo.db['users']
cards_db = mongo.db['cards']


## start `main.py`
from . import main
