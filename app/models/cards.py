import json
from datetime import datetime
from typing import Union
from flask import abort, jsonify, make_response
from bson.objectid import ObjectId

from .. import cards_db
from ..utils import CardCondition, DatabaseOperation, to_bool


class CardModel():
    CardCondition     = CardCondition
    DatabaseOperation = DatabaseOperation

    def __init__(self, parent=None, scryfall_id:str=None, _id:Union[str, ObjectId]=None, user_id:Union[str, ObjectId]=None, amount:Union[int, str]=None, tag:Union[str, dict]=None, foil:bool=None,
                       condition:Union[CardCondition, int, str]=None, signed:bool=None, altered:bool=None, misprint:bool=None, date_created:datetime=None,
                       operation:Union[DatabaseOperation, int, str]=DatabaseOperation.UPDATE, fetch_data_by_id=False):
        '''
        :raises ValueError: when neither `scryfall_id` nor `_id` is provided
        :raises KeyError: when `fetch_data_by_id=True` and `_id` is not found in the database
        :raises EnumParsingError(ValueError): when `condition` or `operation` cant be parsed to its enum counterpart
        :raises bson.errors.InvalidId: when `_id` is not a valid ObjectId
        '''
        data = None
        if not (_id or scryfall_id):
                raise ValueError('Either `_id` or `scryfall_id` must be provided')
            # abort(make_response(
            #     jsonify({
            #         'msg': 'Either `_id` or `scryfall_id` must be provided',
            #     }),
            #     400
            # ))
        if fetch_data_by_id:
            if not _id:
                raise ValueError('`_id` must be provided when using `fetch_data_by_id=True`')
            data = self.get_card_data_by_id(_id)
        if isinstance(amount, str):
            amount = amount.replace(' ','')
        if user_id is None:
            user_id = parent.user_id

        self.parent = parent
        self.user_id = ObjectId(user_id) if user_id else user_id
        self._id = ObjectId(_id) if _id else _id
        self.operation = DatabaseOperation.parse(operation)
        
        if data:
            self.scryfall_id = data['scryfall_id']
            self.amount = data['amount']
            self.tag = data['tag']
            self.foil = data['foil']
            self.condition = CardCondition.parse(data['condition'])
            self.signed = data['signed']
            self.altered = data['altered']
            self.misprint = data['misprint']
            self.date_created = data['date_created']
        else:
            self.scryfall_id = scryfall_id
            self.amount = amount
            self.tag = tag
            self.foil = foil
            self.condition = CardCondition.parse(condition)
            self.signed = signed
            self.altered = altered
            self.misprint = misprint
            self.date_created = date_created
        
    @classmethod
    def get_card_data_by_id(cls, card_id:Union[ObjectId, str]):
        data = cards_db.find_one(
            { '_id': ObjectId(card_id) }
        )
        if data:
            return data
        # else:
        raise KeyError(f'No card with id `{card_id}` found')

    def find_duplicate(self):
        '''
        Looks for a duplication of `self` in the database, excluding `{self._id, self.amount}` while searching.
        Default values are used if `None` is found.
        
        :return: `CardModel` if duplicate is found, otherwise returns None.
        '''
        data = self.to_JSON(to_mongo=True, drop_cols=['_id', 'amount'])
        res = cards_db.find_one(
            { **data }
        )
        if res:
            return CardModel(self.parent, **res)
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
        
        card = self.to_JSON(drop_cols=['_id', 'amount', 'operation'])
        other = other.to_JSON(drop_cols=['_id', 'amount', 'operation'])
        
        return card == other

    def generate_id(self):
        '''
        Generates a random id for this `CardModel` instance and applies it to the card.
        Sets `self.operation` to `CREATE`.

        :return: A updated `CardModel` instance
        '''
        self._id = ObjectId()
        self.operation = DatabaseOperation.CREATE
        return self

    def to_JSON(self, to_mongo=False, drop_cols=[]):
        '''
        JSON representation of this `CardModel`, used for JSON serialization.
        '''
        res = {
            '_id': self._id if to_mongo else str(self._id),
            'user_id': self.user_id if to_mongo else str(self.user_id),
            'scryfall_id': self.scryfall_id,
            'amount': self.amount or 1,
            'tag': self.tag or [],
            'foil': self.foil or False,
            'condition': self.condition.name if self.condition else CardCondition['NM'].name,
            'signed': self.signed or False,
            'altered': self.altered or False,
            'misprint': self.misprint or False,
            'date_created': self.date_created if to_mongo else self.date_created.replace(microsecond=0).isoformat(),
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
            'user_id': self.user_id,
            'scryfall_id': self.scryfall_id,
            'amount': self.amount,
            'tag': self.tag,
            'foil': self.foil,
            'condition': self.condition,
            'signed': self.signed,
            'altered': self.altered,
            'misprint': self.misprint,
            'date_created': self.date_created,
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
        self.tag = self.tag or []
        self.foil = self.foil or False
        self.condition = self.condition or CardCondition['NM']
        self.signed = self.signed or False
        self.altered = self.altered or False
        self.misprint = self.misprint or False
        # self.date_created = self.date_created or datetime.now()
        return self

    def update(self, **kwargs):
        '''
        Updates this `CardModel` instance with the given keyword arguments.
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
            self.operation = DatabaseOperation.UPDATE
        else:
            self.operation = DatabaseOperation.DELETE

        self.scryfall_id = kwargs['scryfall_id'] if 'scryfall_id' in kwargs else self.scryfall_id
        self.tag = kwargs['tag'] if 'tag' in kwargs else self.tag
        self.foil = to_bool(kwargs['foil']) if 'foil' in kwargs else self.foil
        self.condition = CardCondition.parse(kwargs['condition']) if 'condition' in kwargs else self.condition
        self.signed = to_bool(kwargs['signed']) if 'signed' in kwargs else self.signed
        self.altered = to_bool(kwargs['altered']) if 'altered' in kwargs else self.altered
        self.misprint = to_bool(kwargs['misprint']) if 'misprint' in kwargs else self.misprint

        return self

    def delete(self):
        '''
        Marks this `CardModel` instance to be deleted from the collection.
        Does not update the database.
        '''
        self.operation = DatabaseOperation.DELETE
        return self

    def _create(self):
        '''
        Creates a new `CardModel` instance in the database.
        Internal method, should not be called directly, use `CardModel.save()` instead.
        '''
        old_id = self._id
        
        res = cards_db.insert_one(
            {
                **self.to_JSON(to_mongo=True, drop_cols=['_id']),
                'date_created': datetime.now(),
            }
        )
        self._id = res.inserted_id
        
        del self.parent[old_id]
        self.parent[self._id] = self
        
        return res
    
    def _delete(self):
        '''
        Deletes this `CardModel` instance from the database.
        Internal method, should not be called directly, use `CardModel.save()` instead.
        '''
        return cards_db.delete_one(
            { '_id': self._id } # card_id
        )
    
    def _update(self):
        '''
        Updates this `CardModel` instance in the database.
        Internal method, should not be called directly, use `CardModel.save()` instead.
        '''
        return cards_db.update_one(
            { '_id': self._id }, # card_id
            {
                '$set': {
                    **self.to_JSON(to_mongo=True)
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
        res = { }

        if self.operation == DatabaseOperation.NOP:
            res['msg'] = '`_id` not found in collection'
            res['extra_info'] = "when creating a new card, leave it's `_id` field empty"
        elif self.operation == DatabaseOperation.DELETE or self.amount <= 0:
            self._delete()
        elif self.operation == DatabaseOperation.UPDATE:
            self._update()
            res['card'] = self.to_JSON(drop_cols=['user_id'])
        elif self.operation == DatabaseOperation.CREATE:
            if self.operation == DatabaseOperation.CREATE and self.amount <= 0:
                self.operation = DatabaseOperation.NOP
                res['msg'] = '`amount` must be greater than 0 when creating a new card'
            else:
                self._create()
                res['card'] = self.to_JSON(drop_cols=['user_id'])
        else:
            raise Exception('Invalid operation')
                
        res['_id']    = str(self._id)
        res['action'] = self.operation.to_past_tense()
        return res
