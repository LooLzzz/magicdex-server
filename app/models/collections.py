import json, os
from flask import abort, jsonify, make_response
from typing import Iterable, Union, List, Dict
from bson import ObjectId, json_util

from ..utils import DatabaseOperation
from .. import cards_db
from . import CardModel


class CollectionModel():
    def __init__(self, parent):
        self.parent = parent
        self.user_id = self.parent.user_id
        # self._id = data['_id']
        self._cards:Dict[ObjectId, CardModel] = {}
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
            if k not in self._cards:
                self._cards[k] = CardModel(self, _id=k, fetch_data_by_id=True)
        res = { k:v for k,v in self._cards.items() if k in keys }
        return res if isinstance(key, (list, tuple)) else list(res.values())[0]

    def __setitem__(self, key, value):
        self._cards[ObjectId(key)] = value

    def __delitem__(self, key):
        del self._cards[ObjectId(key)]

    def __contains__(self, key):
        return ObjectId(key) in self._cards

    def __iter__(self):
        return iter(self._cards)
    
    def values(self):
        return self._cards.values()
    
    def items(self):
        return self._cards.items()
    
    def keys(self):
        return self._cards.keys()

    def __repr__(self):
        return repr(self._cards)

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
            'user_id': self.user_id if to_mongo else str(self.user_id),
            # 'doc_count': parent.doc_count(),
            'doc_count': len(self._cards),
            'cards': [ card.to_JSON(to_mongo, cards_drop_cols) for card in self._cards.values() ],
        }
        return { k:v for k,v in res.items() if k not in drop_cols }

    def load(self, page:int=1, per_page:int=20, cards:List[CardModel]=[]):
        '''
        Loads cards from the database.

        :param page: Page number
        :param per_page: Number of cards per page
        :param cards: List of cards. To load all cards pass `cards=[]`. Defaults to `[]`
        :return: An updated `CollectionModel` object
        '''
        skip_amount = (page - 1) * per_page
        doc_count = len(cards) if cards else self.parent.doc_count()

        if skip_amount >= doc_count:
            abort(make_response(
                jsonify({
                    'msg': 'pagination page out of bounds',
                    'first_page': f'{os.environ["APP_URL"]}/collections?page=1&per_page={per_page}',
                    'data': []
                }),
                200
            ))
        else:
            data = cards_db \
                .find({
                    'user_id': ObjectId(self.user_id),
                    '_id': { '$in': [ card._id for card in cards ] } if cards
                                                                     else { '$exists': True }
                }) \
                .skip(skip_amount) \
                .limit(per_page)
            self._cards = { item['_id']: CardModel(self, **item) for item in data }
        return self
    
    def load_all(self, cards:List[CardModel]=[]):
        '''
        Loads all cards from the database.
        
        :param cards: List of cards. To load all cards pass `cards=[]`. Defaults to `[]`
        :return: An updated `CollectionModel` object
        '''
        data = cards_db.find({
            'user_id': ObjectId(self.user_id),
            '_id': { '$in': [ card._id for card in cards ] } if cards
                                                             else { '$exists': True }
        })
        self._cards = { item['_id']: CardModel(self, **item) for item in data }
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
            cards = list(self._cards.values())
            for card in cards:
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
                        card.operation = DatabaseOperation.NOP
                        self[card._id] = card
            else:
                # a request to update a card, the card could be an existing one or not
                if dup:
                    # found a card as requested
                    data = card.to_dict(drop_none=True)
                    self[dup._id].update(**data)
                else:
                    # card doesnt exist, create it
                    card = card.none_values_to_default().generate_id()
                    self._cards[card._id] = card
        return self
