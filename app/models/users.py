import re
from datetime import datetime
from typing import Union
from bson import ObjectId
from flask_jwt_extended import create_access_token

from ..utils import UserDoesNotExist, UserAlreadyExists
from .. import bcrypt, users_db, cards_db
from . import CollectionModel


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
    def __init__(self, user_id:Union[ObjectId, str]=None, username:str=None, public:bool=False, **kwargs):
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
            self.public = public
            self.date_created = None
            self.exists = False
        else:
            self.user_id = user['_id']
            self.username = user['username']
            self.password = user['password']
            self.public = user['public']
            self.date_created = user['date_created']
            self.collection = CollectionModel(parent=self)

    def __bool__(self):
        return bool(self.exists)
    
    def doc_count(self):
        '''
        Retrieves the number of document cards in the collection from the database.
        
        :return: Number of document cards in the collection
        '''
        return cards_db.count_documents({ 'user_id': self.user_id })

    @exist_required()
    def check_password_hash(self, password):
        '''
        Tests a password hash against a candidate password. The candidate password is first hashed and then subsequently compared in constant time to the existing hash. This will either return `True` or `False`.

        :param pw_hash: The hash to be compared against
        :param password: The password to compare
        :raises `UserDoesNotExist(ValueError)`: If the user does not exist
        :return: An access token for the user
        '''
        return bcrypt.check_password_hash(self.password, password)

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
        return users_db.find_one({ 'username': { '$regex': f'^{username}$', '$options': 'i' } }) # case insensitive exact match

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
            'public': self.public if self.public else False,
            'date_created': datetime.now(),
        }).inserted_id
        
        return UserModel(user_id=str(user_id))

    @exist_required()
    def to_JSON(self, include_collection=False, to_mongo=False, drop_cols=[], collection_kwarg={}):
        '''
        JSON representation of this `UserModel`, used for JSON serialization.
        '''
        res = {
            'user_id': self.user_id if to_mongo else str(self.user_id),
            'username': self.username,
            'public': self.public,
            'date_created': self.date_created if to_mongo else self.date_created.replace(microsecond=0).isoformat(),
        }
        if include_collection:
            res['collection'] = self.collection.to_JSON(to_mongo=to_mongo, **collection_kwarg)
        return { k:v for k,v in res.items() if k not in drop_cols }

    @exist_required()
    def update(self, **kwargs):
        '''
        Updates this `UserModel` instance with the given keyword arguments.
        Saves the changes to the database.

        :param kwargs: Any `UserModel` properties to update, except [`user_id`, `date_created`]
        :raises UserDoesNotExist: If the user does not exist
        :raises UserAlreadyExists: If the username is already taken
        :return: A Dictionary containing operation info
        '''
        res = []
        
        if 'username' in kwargs:
            if kwargs['username'] != self.username:
                if UserModel.exists(username=kwargs['username']):
                    raise UserAlreadyExists(f"username `{kwargs['username']}` already exists")
                else:
                    self.username = kwargs['username'] if 'username' in kwargs else self.username
                    res += [{ 'field': 'username', 'action': 'UPDATED', 'value': self.username }]
            else:
                res += [{ 'field': 'username', 'action': 'NOP', 'value': self.username }]
            
        
        if 'password' in kwargs:
            if bcrypt.check_password_hash(self.password, kwargs['password']) == False:
                self.password = bcrypt.generate_password_hash(kwargs['password']).decode('utf-8')
                res += [{ 'field': 'password', 'action': 'UPDATED' }]
            else:
                res += [{ 'field': 'password', 'action': 'NOP' }]
            
        if 'public' in kwargs:
            if kwargs['public'] != self.public:
                self.public = kwargs['public'] if 'public' in kwargs else self.public
                res += [{ 'field': 'public', 'action': 'UPDATED', 'value': self.public }]
            else:
                res += [{ 'field': 'public', 'action': 'NOP', 'value': self.public }]
        
        if kwargs:
            update_res = users_db.update_one(
                { '_id': self.user_id }, # user_id
                {
                    '$set': {
                        **self.to_JSON(to_mongo=True, include_collection=False, drop_cols=['user_id']),
                    }
                }
            )
        
        return res
    