from typing import Iterable, Union, List
from bson.objectid import ObjectId

from .. import mongo
from . import CardModel

users_db = mongo.db['users']
collections_db = mongo.db['collections']


class CollectionModel():
    def __init__(self, user_id:Union[ObjectId, str]):
        data = collections_db.find_one(
            # filter
            { 'user_id': ObjectId(user_id) },
            {
                # projection
                '_id': '$_id',
                'user_id': '$user_id',
            }
        )
        if not data:
            raise ValueError('Collection does not exist')

        self._id = data['_id']
        self.user_id = data['user_id']
        self._cards = {}
        # self._cards = { card._id: card for card in [CardModel(parent=self, **item) for item in data['cards']] }

    def __getitem__(self, key):
        if isinstance(key, str):
            # single key
            return self._cards[ObjectId(key)]
        if isinstance(key, Iterable):
            # multiple keys
            keys = [ ObjectId(k) for k in key ]
            return { k:v for k,v in self.items() if k in keys }

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
    
    def keys(self):
        return self._cards.keys()

    def items(self):
        return self._cards.items()

    def __repr__(self):
        return repr(self._cards)

    def to_JSON(self, mongo=False):
        '''
        Converts the collection to a JSON, used for JSON serialization.
        '''
        return {
            '_id': self._id if mongo else str(self._id),
            'user_id': self.user_id if mongo else str(self.user_id),
            'cards': [ card.to_JSON(mongo) for card in self.values() ],
        }

    def find_cid(self, other:CardModel):
        for card in self.values():
            if card == other:
                return card._id
        return None

    @classmethod
    def create(cls, user_id):
        '''
        Creates a new collection and saves it to the database.
        '''
        user_id = ObjectId(user_id)
        collections_db.insert_one({
            'user_id': user_id,
            'cards': [],
        })
        return cls(user_id)

    def save(self):
        '''
        Saves all changes to the collection to the database.
        
        :return: `UpdateResult`
        '''
        cards = [ card.to_JSON(mongo=True) for card in self.values() ]
        newvalues = { "$set": {'cards':cards} }

        res = collections_db.update_one({'_id': self._id}, newvalues, upsert=True)
        return res
    
    def clear(self):
        '''
        Clears the collection.
        Does not update the database.

        :return: An updated `CollectionModel` object
        '''
        self._cards.clear()
        return self
    
    def add(self, card:CardModel):
        if not card._id:
            raise ValueError('Cannot add card without an id')
        if card._id in self:
            raise ValueError('Card id already exists in collection')
        
        card = card.none_values_to_default()
        if card.amount > 0:
            self[card._id] = card
        # else:
        #     raise ValueError('Card amount must be greater than 0')
        
        return self

    # def merge(self, a:CardModel, b:CardModel):
    #     '''
    #     Merges two given cards into one card, result will be put into object `a`.
    #     Does not update the database.

    #     :param a: The id of the first card
    #     :param b: The id of the second card
    #     :return: `ObjectId` of the newly merged card
    #     '''
    #     a.update(b)
    #     del self[b]
    #     return a

    def update(self, cards:List[CardModel]):
        '''
        Updates the collection with the given cards.
        Does not update the database.

        :return: An updated `CollectionModel` object
        '''
        for card in cards:
            cid = card._id
            if cid is None:
                # test if the card already exists in the collection
                # if it does, find its cid
                # if not, generate a cid for it
                cid = self.find_cid(card)
                if cid is None:
                    card.generate_id()
                else:
                    card._id = cid
            
            if cid in self:
                card._id = None
                another_cid = self.find_cid(card)
                
                if another_cid is None:
                    # only one occurences of the card exists in the collection, update it
                    self[cid].update(card)
                else:
                    # two occurences of the same card exist in the collection, merge and update it
                    cid = self.merge(cid, another_cid)
                    self[cid].update(card)
            else:
                # card doesnt exist in the collection, add it
                self.add(card)
        
        return self
