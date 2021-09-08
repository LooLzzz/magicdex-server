import json, os
from flask import abort, jsonify, make_response, request
from urllib.parse import urlparse
from typing import Iterable, Union, List, Dict
from bson import ObjectId, json_util

from ..utils import CardOperation
from .. import cards_db
from . import CardModel


class CollectionModel():
    def __init__(self, parent):
        # data = collections_db.find_one(
        #     { 'user_id': ObjectId(parent.user_id) }, # filter
        #     {
        #         # projection
        #         '_id': 1,
        #         'user_id': 1,
        #     }
        # )
        # if not data:
        #     raise ValueError('Collection does not exist')

        self.parent = parent
        self.user_id = self.parent.user_id
        # self._id = data['_id']
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

    def inc_doc_count(self, amount:int):
        '''
        Increments the number of document cards in the collection by `amount`.

        :param amount: The amount to increment
        :return: The new document count
        '''
        return self.parent.inc_doc_count(amount)

    def to_JSON(self, to_mongo=False, drop_cols=[], cards_drop_cols=[]):
        '''
        JSON representation of this `CollectionModel`, used for JSON serialization.
        '''
        res = {
            # '_id': self._id if to_mongo else str(self._id),
            # '_id': self._id if to_mongo else {'$oid': str(self._id)},
            'user_id': self.user_id if to_mongo else str(self.user_id),
            'doc_count': self.parent.doc_count(),
            'cards': [ card.to_JSON(to_mongo, cards_drop_cols) for card in self.cards.values() ],
        }
        return { k:v for k,v in res.items() if k not in drop_cols }

    def load(self, page:int=1, per_page:int=20):
        '''
        Loads cards from the database.

        :param page: Page number
        :param per_page: Number of cards per page
        :return: An updated `CollectionModel` object
        '''
        skip_amount = (page - 1) * per_page

        if skip_amount >= self.parent.doc_count():
            abort(make_response(
                jsonify({
                    'msg': 'pagination page out of bounds',
                    # 'back_to_start': f'http://{urlparse(request.base_url).hostname}/collections?page=1',
                    # 'back_to_start': request.host_url + 'collections?page=1',
                    'first_page': f'{os.environ["APP_URL"]}/collections?page=1&per_page={per_page}',
                    'data': []
                }),
                200
            ))
        else:
            data = cards_db \
                .find({ 'user_id': ObjectId(self.user_id) }) \
                .skip(skip_amount) \
                .limit(per_page)
            self.cards = { item['_id']: CardModel(self, **item) for item in data }
        return self
    
    def load_all(self):
        '''
        Loads all cards from the database.
        
        :return: An updated `CollectionModel` object
        '''
        data = cards_db.find(
            { 'user_id': ObjectId(self.user_id) }
        )
        self.cards = { item['_id']: CardModel(self, **item) for item in data }
        return self

    @classmethod
    def create(cls, user_id:Union[ObjectId, str]):
        '''
        Creates a new collection and saves it to the database.

        :param user_id: The id of the user that owns the collection
        :returns: `InsertOneResult` object
        '''
        return { 'msg': '`CollectionModel.create()` method is deprecated' }
        # return collections_db.insert_one({
        #     'user_id': ObjectId(user_id),
        #     'cards': [],
        # })

    def save(self):
        '''
        Saves all changes to the collection to the database.
        
        :return: List of result objects
        '''
        res = []
        
        if self.clear_db:
            self.clear_db = False
            cards = cards_db.find(
                { 'user_id': ObjectId(self.user_id) },
                { '_id': 1 }
            )
            delete_res = cards_db.delete_many({
                '_id': {
                    '$in': [ item['_id'] for item in cards ]
                }
            })
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
                # a request to update a specific card_id
                if dup:
                    if card._id == dup._id:
                        # found the same card_id as the request
                        data = card.to_dict(drop_none=True)
                        self[dup._id].update(**data)
                    else:
                        # found the same card as the request, but with a different id
                        data = dup.to_dict(drop_none=True)
                        self[card._id].update(**data) # keep the requested card
                        self[dup._id].delete() # remove the duplicate
                else:
                    try:
                        data = card.to_dict(drop_none=True)
                        self[card._id].update(**data) # will raise a key error if card_id is not present in the database
                    except KeyError:
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
                    card.amount = int(card.amount) if int(card.amount) > 0 else 1
                    card.generate_id()
                    self[card._id] = card
        return self
