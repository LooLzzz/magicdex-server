import os
from datetime import timedelta
from typing import TypeVar

from motor import core as motor_core
from motor import motor_asyncio
from passlib.context import CryptContext
from pydantic import BaseModel

_DocType = TypeVar('_DocType', bound=BaseModel)

# cryptoghraphy
ACCESS_TOKEN_EXPIRE = timedelta(weeks=4)
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
crypt_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto'
)

# monogdb
MONGODB_URL = os.getenv('MONGODB_URL')
mongodb_client: motor_core.AgnosticClient = motor_asyncio.AsyncIOMotorClient(
    MONGODB_URL,
    tls=True,
    tlsAllowInvalidCertificates=True
)
users_collection: motor_core.Collection[_DocType] = mongodb_client['magicdex-db']['users']
cards_collection: motor_core.Collection[_DocType] = mongodb_client['magicdex-db']['cards']
