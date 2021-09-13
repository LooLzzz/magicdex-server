import re
from datetime import datetime
from typing import Union, List
from bson import ObjectId
from flask_jwt_extended import create_access_token
from pymongo import ReturnDocument

from ..utils import UserDoesNotExist, UserAlreadyExists
from .. import bcrypt, users_db
from . import CollectionModel, CardModel


def exist_required(invert=False):
    '''
    A wrapper for rasing an exception if the user does/doesnt exist.

    :param invert: If True, the exception is raised if the user does exist.
    '''
    def outer(func):
        def inner(self, *args, **kwargs):
            if invert:
                if self:
                    raise UserAlreadyExists
            else:
                if not self:
                    raise UserDoesNotExist
            return func(self, *args, **kwargs)
        return inner
    return outer


class UserModel():
    def __init__(self, user_id:Union[ObjectId, str]=None, username:str=None):
        '''
        Intitates a user.
        If the user doesnt exists, `bool(self)` will be set to False and any subsequent operation will raise an exception.
        '''
        if not (bool(user_id) != bool(username)): # not xor
            raise ValueError('Please provide either username or user_id')
        
        user = self.exists(user_id, username)
        if not user:
            self.user_id = user_id
            self.username = username
            self.exists = False
        else:
            self.user_id = user['_id']
            self.username = user['username']
            self.password_hash = user['password']
            self.collection = CollectionModel(parent=self)

    def __bool__(self):
        return bool(self.exists)
    
    def doc_count(self):
        '''
        Retrieves the number of document cards in the collection from the database.
        
        :return: Number of document cards in the collection
        '''
        data = users_db.find_one(
            { '_id': ObjectId(self.user_id) } # filter
        )
        return data['doc_count']

    def inc_doc_count(self, amount:int):
        '''
        Increments the number of document cards in the collection by `amount`.

        :param amount: The amount to increment
        :return: The new document count
        '''
        res = users_db.find_one_and_update(
            filter = { '_id': self.user_id },
            update = {
                '$inc': {
                    'doc_count': amount
                }
            },
            return_document = ReturnDocument.AFTER
        )
        return res['doc_count']

    @exist_required()
    def check_password_hash(self, password):
        '''
        Tests a password hash against a candidate password. The candidate password is first hashed and then subsequently compared in constant time to the existing hash. This will either return `True` or `False`.

        :param pw_hash: The hash to be compared against
        :param password: The password to compare
        :raises `UserDoesNotExist(ValueError)`: If the user does not exist
        :return: An access token for the user
        '''
        return bcrypt.check_password_hash(self.password_hash, password)

    @exist_required()
    def create_access_token(self):
        '''
        Creates an access token for the user.

        :raises `UserDoesNotExist(ValueError)`: If the user does not exist
        :return: An access token for the user
        '''
        access_token = create_access_token(
            identity = ( str(self.user_id), self.username )
        )
        # return 'Bearer {access_token}'
        return access_token

    @classmethod
    def exists(cls, user_id:Union[ObjectId, str]=None, username:str=None):
        '''
        Checks if a user exists in the database
        
        :param user_id: The user's id
        :param username: The user's username
        :return: `mongo.find_one()` results
        '''
        if not (bool(user_id) != bool(username)): # not xor
            raise ValueError('Please provide either username or user_id')

        if user_id:
            return users_db.find_one({ '_id': ObjectId(user_id) })
        # elif username:
        return users_db.find_one({ 'username': re.compile(username, re.IGNORECASE) })

    @exist_required(invert=True)
    def create(self, password):
        '''
        Creates a new user.
        
        :param username: The user's username
        :param password: The user's password
        :raises `UserAlreadyExists(ValueError)`: If the username is already taken
        :return: A new `UserModel` instance of the newly created user
        '''
        user_id = users_db.insert_one({
            'username': self.username,
            'password': bcrypt.generate_password_hash(password).decode('utf-8'),
            'date': datetime.now(),
            'doc_count': 0
        }).inserted_id
        
        # CollectionModel.create(user_id)
        return UserModel(user_id=str(user_id))
