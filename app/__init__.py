import os

import dotenv
from fastapi import FastAPI
from motor import core as motor_core
from motor import motor_asyncio

from .models import Card, User

# dotenv
dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')

# fastapi
app = FastAPI()

# monogdb
mongodb_client: motor_core.AgnosticClient = motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL,
    tls=True,
    tlsAllowInvalidCertificates=True
)
users_collection: motor_core.Collection['User'] = mongodb_client['magicdex-db']['users']
cards_collection: motor_core.Collection['Card'] = mongodb_client['magicdex-db']['cards']

# start `main.py` !important
from . import main
