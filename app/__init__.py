import os, dotenv, certifi
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt import JWT
from flask_pymongo import PyMongo
from flask_restful import Api


## load `.env` file if exists
env_filepath = dotenv.find_dotenv('.env')
if os.path.exists(env_filepath):
    dotenv.load_dotenv(env_filepath)


## create flask app
app = Flask(__name__)
api = Api(app)


## config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_RW_URI')


## addons
mongo = PyMongo(app, tlsCAFile=certifi.where())
bcrypt = Bcrypt(app)
# jwt = JWT(app)


## start `main.py`
from . import main