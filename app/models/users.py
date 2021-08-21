import re
from datetime import datetime
from typing import Union
from bson.objectid import ObjectId
from flask_jwt_extended import create_access_token

from .. import mongo, bcrypt
from . import CollectionModel

users_db = mongo.db['users']
collections_db = mongo.db['collections']

class UserDoesNotExist(ValueError):
    pass
class UserAlreadyExist(ValueError):
    pass

def exist_required(func):
    '''
    A wrapper for rasing an exception if the user does not exist.
    '''
    def wrapper(self, *args, **kwargs):
        if not self:
            raise UserDoesNotExist('User doesnt exist', f'"{self.username}"' if self.username else '')
        return func(self, *args, **kwargs)
    return wrapper

class UserModel():
    def __init__(self, user_id:Union[ObjectId, str]=None, username:str=None):
        '''
        Intitates a user.
        If the user doesnt exists, `bool(self)` will be set to False and any subsequent operation will raise an exception.
        '''
        if not (user_id != username): # not xor
            raise ValueError('Please provide either username or user_id')
        
        user = self.exists(user_id, username)
        if not user:
            self.exists = False
        else:
            self.user_id = user['_id']
            self.username = user['username']
            self.password_hash = user['password']
            # self.collection = CollectionModel(self.user_id)

    def __bool__(self):
        return bool(self.exists)
    
    @exist_required
    def check_password_hash(self, password):
        '''
        Tests a password hash against a candidate password. The candidate password is first hashed and then subsequently compared in constant time to the existing hash. This will either return `True` or `False`.

        :param pw_hash: The hash to be compared against
        :param password: The password to compare
        :raises ValueError: If the user does not exist
        :return: An access token for the user
        '''
        return bcrypt.check_password_hash(self.password_hash, password)

    @exist_required
    def create_access_token(self):
        '''
        Creates an access token for the user.

        :raises ValueError: If the user does not exist
        :return: An access token for the user
        '''
        return create_access_token(identity=( str(self.user_id), self.username ))

    @classmethod
    def exists(cls, user_id:Union[ObjectId, str]=None, username:str=None):
        '''
        Checks if a user exists in the database
        
        :param user_id: The user's id
        :param username: The user's username
        :return: `mongo.find_one()` results
        '''
        if not (user_id != username): # not xor
            raise ValueError('Please provide either username or user_id')

        if user_id:
            return users_db.find_one({ '_id': user_id })
        # elif username:
        return users_db.find_one({ 'username': re.compile(username, re.IGNORECASE) })

    @classmethod
    def create(cls, username, password):
        '''
        Creates a new user.
        
        :param username: The user's username
        :param password: The user's password
        :raises ValueError: If the username is already taken
        :return: A `UserModel` instance
        '''
        if cls.exists(username=username):
            raise UserAlreadyExist('User already exists')
        
        user_id = users_db.insert_one({
            'username': username,
            'password': bcrypt.generate_password_hash(password).decode('utf-8'),
            'date': datetime.now()
        }).inserted_id
        
        CollectionModel.create(user_id)
        return cls(user_id)