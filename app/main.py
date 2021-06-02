import os, dotenv, certifi
from bson.json_util import dumps
from flask import Flask
from flask_pymongo import PyMongo

# env_filepath = dotenv.find_dotenv('.env')
env_filepath = os.path.realpath('.env')
if os.path.exists(env_filepath):
    dotenv.load_dotenv(env_filepath)

app = Flask(__name__)

# app.config['MONGO_URI'] = os.environ.get('MONGO_RW_URI')
app.config['MONGO_URI'] = os.getenv('MONGO_R_URI')
mongo = PyMongo(app, tlsCAFile=certifi.where())

@app.route('/')
def index():
    res = mongo.db['users'].find_one({'username':'admin'})
    # res = dumps(res['username'])
    return res['username']
