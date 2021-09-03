import json
from typing import Iterable, Union, List, Dict
from bson import ObjectId, json_util

from ..utils import CardOperation
from .. import collections_db
from . import CardModel


class CollectionModel():
    def __init__(self, parent):
        data = collections_db.find_one(
            # filter
            { 'user_id': ObjectId(parent.user_id) },
            {
                # projection
                '_id': 1,
                'user_id': 1,
            }
        )
        if not data:
            raise ValueError('Collection does not exist')

        self.parent = parent
        self.user_id = self.parent.user_id
        self._id = data['_id']
        self.cards:Dict[ObjectId, CardModel] = {}
        # self.cards = { card._id: card for card in [CardModel(parent=self, **item) for item in data['cards']] }
        self.clear_db = False

    def __getitem__(self, key):
        if isinstance(key, (ObjectId, str)):
            keys = [ ObjectId(key) ]
        elif isinstance(key, (list, tuple)):
            keys = [ ObjectId(k) for k in key ]
        else: # if not isinstance(key, Iterable):
            raise ValueError(f'Invalid key type {type(key)}')

        for k in keys:
            if k not in self.cards:
                self.cards[k] = CardModel(self, _id=k, fetch_data_by_id=True)
        res = { k:v for k,v in self.cards.items() if k in keys }
        return res if isinstance(key, (list, tuple)) else list(res.values())[0]

    def __setitem__(self, key, value):
        self.cards[ObjectId(key)] = value

    def __delitem__(self, key):
        del self.cards[ObjectId(key)]

    def __contains__(self, key):
        return ObjectId(key) in self.cards

    def __iter__(self):
        return iter(self.cards)
    
    def values(self):
        return self.cards.values()
    
    def items(self):
        return self.cards.items()
    
    def keys(self):
        return self.cards.keys()

    def __repr__(self):
        return repr(self.cards)

    def to_JSON(self, to_mongo=False, drop_cols=[], cards_drop_cols=[]):
        '''
        JSON representation of this `CollectionModel`, used for JSON serialization.
        '''
        res = {
            '_id': self._id if to_mongo else str(self._id),
            # '_id': self._id if to_mongo else {'$oid': str(self._id)},
            'user_id': self.user_id if to_mongo else str(self.user_id),
            'cards': [ card.to_JSON(to_mongo, cards_drop_cols) for card in self.cards.values() ],
        }
        return { k:v for k,v in res.items() if k not in drop_cols }

    def load_all(self):
        '''
        Loads all cards from the database.
        
        :return: An updated `CollectionModel` object
        '''
        data = collections_db.find_one(
            { 'user_id': ObjectId(self.user_id) }, # filter
            { 'cards': 1 } # projection
        )
        self.cards = { item['_id']: CardModel(self, **item) for item in data['cards'] }
        return self

    @classmethod
    def create(cls, user_id:Union[ObjectId, str]):
        '''
        Creates a new collection and saves it to the database.

        :param user_id: The id of the user that owns the collection
        :returns: `InsertOneResult` object
        '''
        return collections_db.insert_one({
            'user_id': ObjectId(user_id),
            'cards': [],
        })

    def save(self):
        '''
        Saves all changes to the collection to the database.
        
        :return: List of result objects
        '''
        res = []
        
        if self.clear_db:
            self.clear_db = False
            cards = collections_db.find_one_and_update(
                { '_id': ObjectId(self._id) },
                { '$set': { 'cards': [] } }
            )['cards']
            # self.cards = { item['_id']:CardModel(parent=self, operation=CardOperation.DELETE, **item) for item in cards }
            for item in cards:
                res += [{
                    '_id': item['_id'],
                    'action': 'DELETED'
                }]
        else:
            for card in self.cards.values():
                res += [ card.save() ]
        
        return res
    
    def clear(self):
        '''
        Clears the collection from the database.
        Does not update the database by itself.
        `.save()` should be called in order to update the database.

        :return: An updated `CollectionModel` object
        '''
        # self.cards.clear()
        self.clear_db = True

        return self

    def update(self, cards:List[CardModel]):
        '''
        Updates the collection with the given cards.
        Does not update the database.

        :param cards: A list of `CardModel` to be added or updated
        :return: An updated `CollectionModel` object
        '''
        for card in cards:
            dup = card.find_duplicate()
            if card._id is not None:
                # a request to update a specific card id
                if dup:
                    if card._id == dup._id:
                        # found the same card id as the request
                        data = card.to_dict(drop_none=True)
                        self[dup._id].update(**data)
                    else:
                        # found the same card as the request, but with a different id
                        data = dup.to_dict(drop_none=True)
                        self[card._id].update(**data) # keep the requested card
                        self[dup._id].operation = CardOperation.DELETE # remove the duplicate
                else:
                    # requested id doesnt exist
                    card.operation = CardOperation.NOP
                    self[card._id] = card
            else:
                # a request to update a card, the card could be an existing one or not
                if dup:
                    # found a card as requested
                    data = card.to_dict(drop_none=True)
                    self[dup._id].update(**data)
                else:
                    # card doesnt exist, create it
                    card.generate_id()
                    card.amount = int(card.amount)
                    card.operation = CardOperation.CREATE
                    self[card._id] = card
        
        return self
