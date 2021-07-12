import os, dotenv, certifi
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_pymongo import PyMongo
from flask_restful import Api
from flask_sslify import SSLify


## load `.env` file if exists
env_filepath = dotenv.find_dotenv('.env')
if os.path.exists(env_filepath):
    dotenv.load_dotenv(env_filepath)


## create flask app
app = Flask(__name__)

## config stuff
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_RW_URI')


## addons
sslify = SSLify(app)
mongo = PyMongo(app, tlsCAFile=certifi.where())
bcrypt = Bcrypt(app)
api = Api(app)
jwt = JWTManager(app)

## start `main.py`
from . import main
