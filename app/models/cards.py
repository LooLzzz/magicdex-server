import json
from typing import Union
from bson import json_util
from bson.objectid import ObjectId

from .. import collections_db
from ..utils import CardCondition, CardOperation, to_bool


class CardModel():
    CardCondition = CardCondition
    CardOperation = CardOperation

    def __init__(self, parent=None, scryfall_id:str=None, _id:Union[str, ObjectId]=None, amount:Union[int, str]='+1', tag:Union[str, dict]=None, foil:bool=None,
                       condition:Union[CardCondition, int, str]=None, signed:bool=None, altered:bool=None, misprint:bool=None,
                       operation:Union[CardOperation, int, str]=CardOperation.UPDATE, fetch_data_by_id=False):
        data = None
        # if not (_id or scryfall_id):
        #     raise ValueError('Either _id or scryfall_id must be provided')
        if fetch_data_by_id:
            if not _id:
                raise ValueError('Either _id or must be provided when using `fetch_data_by_id=True`')
            data = self.get_card_data_by_id(parent.user_id, _id)
        if isinstance(amount, str):
            amount = amount.replace(' ','')

        self.parent = parent
        self._id = ObjectId(_id) if _id else _id
        self.scryfall_id = data['scryfall_id'] if data else scryfall_id
        self.amount = data['amount'] if data else amount
        self.tag = data['tag'] if data else tag
        self.foil = data['foil'] if data else foil
        self.condition = CardCondition.parse(data['condition'] if data else condition)
        self.signed = data['signed'] if data else signed
        self.altered = data['altered'] if data else altered
        self.misprint = data['misprint'] if data else misprint
        self.operation = CardOperation.parse(operation)

    @classmethod
    def get_card_data_by_id(cls, user_id:Union[ObjectId, str], card_id:Union[ObjectId, str]):
        data = collections_db.find_one(
            {
                'user_id': ObjectId(user_id)
            },
            {
                'cards': {
                    '$elemMatch': {
                        '_id': ObjectId(card_id)
                    }
                }
            }
        )
        if data and 'cards' in data and len(data['cards']) > 0: # all the validations!
            return data['cards'][0]
        else:
            raise KeyError(f'No card with id `{card_id}` found')
        # return cls(**data['cards'])

    def find_duplicate(self):
        '''
        Looks for a duplication of `self`, excluding `{self._id, self.amount}` while searching.
        Default values are used if `None` is found.
        
        :return: `CardModel` if duplicate is found, otherwise returns None.
        '''
        data = self.to_JSON(to_mongo=True, drop_cols=['_id', 'amount'])
        res = collections_db.find_one(
            {
                'user_id': self.parent.user_id, # user_id
            },
            {
                'cards': {
                    '$elemMatch': {
                        **data
                    }
                }
            }
        )
        if res and 'cards' in res and len(res['cards']) > 0: # all the validations!
            return CardModel(self.parent, **res['cards'][0])
        return None

    def __getitem__(self, key):
        if isinstance(key, str):
            keys = [ key ]
        elif isinstance(key, (list, tuple)):
            keys = key
        else: #if not isinstance(key, (list, tuple)):
            raise ValueError(f'Invalid key type {type(key)}')

        res = {}
        for k in keys:
            res[k] = getattr(self, k)
        return res if isinstance(key, (list, tuple)) else list(res.values())[0]

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __eq__(self, other:'CardModel'):
        if self._id == other._id:
            return True
        
        del_keys = ['_id', 'amount', 'operation']
        card = self.to_JSON(drop_cols=del_keys)
        other = other.to_JSON(drop_cols=del_keys)
        
        return card == other

    def generate_id(self):
        '''
        Generates a random id for this `CardModel` instance and applies it to the card.
        Sets `self.operation` to `CREATE`.

        :return: A updated `CardModel` instance
        '''
        self._id = ObjectId()
        self.operation = CardOperation.CREATE
        return self

    def to_JSON(self, to_mongo=False, drop_cols=[]):
        '''
        JSON representation of this `CardModel`, used for JSON serialization.
        '''
        res = {
            '_id': self._id if to_mongo else str(self._id),
            # '_id': self._id if to_mongo else {'$oid': str(self._id)},
            'scryfall_id': self.scryfall_id,
            'amount': self.amount if self.amount else 1,
            'tag': self.tag if self.tag else [],
            'foil': self.foil if self.foil else False,
            'condition': self.condition.name if self.condition else CardCondition['NM'].name,
            'signed': self.signed if self.signed else False,
            'altered': self.altered if self.altered else False,
            'misprint': self.misprint if self.misprint else False,
        }
        return { k:v for k,v in res.items() if k not in drop_cols }

    def to_dict(self, drop_cols=[], drop_none=False):
        '''
        Dictionary representation of this `CardModel` instance
        
        :param drop_cols: A list of columns to drop from the returned dictionary, defaults to `[]`
        :param drop_none: A boolean flag to drop columns with `None` values, defaults to `False`
        :return: A dictionary representation of this `CardModel` instance
        '''
        res = {
            '_id': self._id,
            'scryfall_id': self.scryfall_id,
            'amount': self.amount,
            'tag': self.tag,
            'foil': self.foil,
            'condition': self.condition,
            'signed': self.signed,
            'altered': self.altered,
            'misprint': self.misprint,
            'operation': self.operation,
        }
        res = { k:v for k,v in res.items() if v is not None } if drop_none else res
        res = { k:v for k,v in res.items() if k not in drop_cols }
        return res

    def __repr__(self):
        return repr(self.to_dict())
    
    def none_values_to_default(self):
        '''
        Sets all `None` attribute values to their default ones.
        
        :return: An updated `CardModel` instance
        '''
        self.amount = int(self.amount) if self.amount else 1
        self.tag = self.tag if self.tag else []
        self.foil = self.foil if self.foil else False
        self.condition = self.condition if self.condition else CardCondition['NM']
        self.signed = self.signed if self.signed else False
        self.altered = self.altered if self.altered else False
        self.misprint = self.misprint if self.misprint else False
        return self

    def update(self, **kwargs):
        '''
        Updates this `CardModel` instance with the values from another `CardModel` instance.
        If `amount > 0` self.operation will be set to `UPDATE`, otherwise it will be set to `DELETE`

        :param kwargs: Any `CardModel` properties to update
        :return: An updated `CardModel` instance
        '''
        if 'amount' in kwargs:
            amount = str(kwargs['amount'])
            if amount[0] in {'+', '-'}:
                self.amount += int(amount)
            else:
                self.amount = int(amount)
        if self.amount > 0:
            self.operation = CardOperation.UPDATE
        else:
            self.operation = CardOperation.DELETE

        self.scryfall_id = kwargs['scryfall_id'] if 'scryfall_id' in kwargs else self.scryfall_id
        self.tag = kwargs['tag'] if 'tag' in kwargs else self.tag
        self.foil = to_bool(kwargs['foil']) if 'foil' in kwargs else self.foil
        self.condition = str(CardCondition.parse(kwargs['condition'])) if 'condition' in kwargs else self.condition
        self.signed = to_bool(kwargs['signed']) if 'signed' in kwargs else self.signed
        self.altered = to_bool(kwargs['altered']) if 'altered' in kwargs else self.altered
        self.misprint = to_bool(kwargs['misprint']) if 'misprint' in kwargs else self.misprint

        return self

    def delete(self):
        '''
        Marks this `CardModel` instance to be deleted from the collection.
        Does not update the database.
        '''
        self.operation = CardOperation.DELETE
        return self

    def _create(self):
        '''
        Creates a new `CardModel` instance in the database.
        Internal method, should not be called directly.
        '''
        return collections_db.update_one(
            {
                # '_id': self.parent._id, # collection_id
                'user_id': self.parent.user_id, # user_id
            },
            {
                '$push': {
                    'cards': self.to_JSON(to_mongo=True)
                }
            }
        )
    
    def _delete(self):
        '''
        Deletes this `CardModel` instance from the database.
        Internal method, should not be called directly.
        '''
        return collections_db.update_one(
            {
                # '_id': self.parent._id, # collection_id
                'user_id': self.parent.user_id, # user_id
            },
            {
                '$pull': {
                    'cards': {
                        '_id': self._id # card_id
                    }
                }
            }
        )
    
    def _update(self):
        '''
        Updates this `CardModel` instance in the database.
        Internal method, should not be called directly.
        '''
        return collections_db.update_one(
            {
                # '_id': self.parent._id, # collection_id
                'user_id': self.parent.user_id, # user_id
                'cards._id': self._id # card_id
            },
            {
                '$set': {
                    'cards.$': self.to_JSON(to_mongo=True)
                }
            }
        )

    def save(self):
        '''
        Saves this `CardModel` instance to the database.
        Calls `_create()`, `_update()` or `_delete()` internally.
        
        :raises Exception: If the operation fails
        :return: A Dictionary containing operation info
        '''
        res = {
            '_id': str(self._id),
            'action': self.operation.to_past_tense()
        }
        if self.operation == CardOperation.NOP:
            res['msg'] = '`_id` not found in collection'
            res['help'] = "when creating a new card, leave it's `_id` field empty"
        elif self.operation == CardOperation.DELETE or self.amount <= 0:
            self._delete()
        elif self.operation == CardOperation.UPDATE:
            self._update()
        elif self.operation == CardOperation.CREATE:
            self._create()
        else:
            raise Exception('Invalid operation')
        return res
