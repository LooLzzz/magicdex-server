from enum import Enum
from typing import Union
from bson.objectid import ObjectId

from .. import mongo

users_db = mongo.db['users']
collections_db = mongo.db['collections']


class Condition(Enum):
    NM      = 0
    LP      = 1
    MP      = 2
    HP      = 3
    DAMAGED = 4

    @classmethod
    def parse(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        if isinstance(value, str):
            try:
                return cls(int(value))
            except ValueError:
                value = value.replace(' ', '_').upper()
                if '_' in value:
                    value = ''.join([ word[0] for word in value.split('_') ]) # NEAR_MINT -> NM
                return cls[value]
        
        raise ValueError(f'Unable to parse value to Condition Enum: {value}')


class Card():
    def __init__(self, parent, card_id:str=None, scryfall_id:str=None, _id:Union[str, ObjectId]=None, amount:Union[int, str]='+1', tag:Union[str, dict]=None, foil:bool=None,
                       condition:Union[Condition, int, str]=None, signed:bool=None, altered:bool=None, misprint:bool=None):
        if not (_id or card_id or scryfall_id):
            raise ValueError('Either _id, card_id or scryfall_id must be provided')
        if _id and not (scryfall_id or card_id):
            doc = collections_db.find_one({'cards._id': ObjectId(_id)})['cards']
            scryfall_id = [ card['scryfall_id'] for card in doc if card['_id'] == ObjectId(_id) ][0]
            

        self.parent = parent
        self._id = ObjectId(_id) if _id else None
        self.scryfall_id = scryfall_id if scryfall_id else card_id
        self.amount = amount.replace(' ','') if isinstance(amount, str) else amount
        self.tag = tag
        self.foil = foil
        self.condition = Condition.parse(condition) if condition else None
        self.signed = signed
        self.altered = altered
        self.misprint = misprint

    def __getitem__(self, key):
        key = 'scryfall_id' if key == 'card_id' else key # change all occurences of `card_id` to `scryfall_id`
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __eq__(self, other:'Card'):
        if self._id == other._id:
            return True
        
        other = other.to_JSON()
        card = self.to_JSON()
        del other['_id']
        del other['amount']
        del card['_id']
        del card['amount']
        
        return card.items() == other.items()

    def generate_id(self):
        '''
        Generates a random id for this `Card` instance and applies it to the card.

        :return: A random 12-byte `ObjectId`
        '''
        self._id = ObjectId()
        return self._id

    def to_JSON(self, mongo=False):
        '''
        Converts the collection to a JSON, used for JSON serialization.
        '''
        return {
            '_id': self._id if mongo else str(self._id),
            'scryfall_id': self.scryfall_id,
            'amount': self.amount if self.amount else 1,
            'tag': self.tag if self.tag else [],
            'foil': self.foil if self.foil else False,
            'condition': self.condition.name if self.condition else Condition['NM'].name,
            'signed': self.signed if self.signed else False,
            'altered': self.altered if self.altered else False,
            'misprint': self.misprint if self.misprint else False,
        }

    def __repr__(self):
        return repr({
            '_id': self._id,
            'scryfall_id': self.scryfall_id,
            'amount': self.amount,
            'tag': self.tag,
            'foil': self.foil,
            'condition': self.condition,
            'signed': self.signed,
            'altered': self.altered,
            'misprint': self.misprint,
        })
    
    def none_to_default_values(self):
        self.amount = int(self.amount) if self.amount else 1
        self.tag = self.tag if self.tag else []
        self.foil = self.foil if self.foil else False
        self.condition = self.condition if self.condition else Condition['NM']
        self.signed = self.signed if self.signed else False
        self.altered = self.altered if self.altered else False
        self.misprint = self.misprint if self.misprint else False
        return self

    def update(self, card:'Card'):
        # if self._id != card._id:
        #     raise ValueError('Cannot update card with different id')
        
        if card.amount:
            amount = str(card.amount)
            if amount[0] in {'+', '-'}:
                self.amount += int(amount)
            else:
                self.amount = int(amount)
        
        if self.amount <= 0:
            self.parent.remove(self._id)

        self.tag = card.tag if card.tag is not None else self.tag
        self.foil = card.foil if card.foil is not None else self.foil
        self.condition = card.condition if card.condition is not None else self.condition
        self.signed = card.signed if card.signed is not None else self.signed
        self.altered = card.altered if card.altered is not None else self.altered
        self.misprint = card.misprint if card.misprint is not None else self.misprint
