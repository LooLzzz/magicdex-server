from datetime import datetime
from typing import Any, Literal, Union, overload
from uuid import UUID

from pydantic import Field, PositiveInt, validator

from .utils import AmountInt, CustomBaseModel, MongoModel, PyObjectId


class Card(MongoModel):
    user_id: PyObjectId
    scryfall_id: UUID
    amount: PositiveInt
    tag: list[str]
    foil: bool
    condition: Literal['NM', 'LP', 'MP', 'HP', 'DAMAGED']
    signed: bool
    altered: bool
    misprint: bool
    date_created: datetime = Field(default_factory=datetime.utcnow)

    def update(self, aggregate: bool = False, inplace: bool = False, **kwargs) -> 'Card':
        if inplace:
            res = self
        else:
            res = super().copy()

        amount: AmountInt
        match kwargs:
            case {'amount': amount} if amount.is_relative() or aggregate:
                res.amount += amount
            case {'date_created': date_created, 'user_id': user_id}:
                """ignore"""
            case {**rest}:
                for k, v in rest.items():
                    setattr(res, k, v)
        return res

    def _equals(self,
                other, *,
                ignore_userid: bool = True,
                ignore_cardid: bool = True) -> bool:
        if not isinstance(other, Card):
            return False

        exclude = set()
        if ignore_userid:
            exclude.add('user_id')
        if ignore_cardid:
            exclude.add('id')

        a = self.dict(exclude=exclude)
        b = other.dict(exclude=exclude)
        return a == b

    def __eq__(self, other) -> bool:
        return self._equals(other)

    def __ne__(self, other) -> bool:
        return not self._equals(other)


class CardUpdateRequest(CustomBaseModel):
    id: PyObjectId = Field(alias='_id')
    amount: AmountInt | None = None
    tag: list[str] | None = None
    foil: bool | None = None
    condition: Literal['NM', 'LP', 'MP', 'HP', 'DAMAGED'] | None = None
    signed: bool | None = None
    altered: bool | None = None
    misprint: bool | None = None

    class Config:
        schema_extra = {
            'example': {
                'id': '62893131e783d76debacbde6',
                'amount': '+4',
                'tag': ['zurgo edh', 'turtles'],
                'foil': True,
                'condition': 'NM',
                'signed': False,
                'altered': False,
                'misprint': False,
            }
        }


class CardRequestNoId(CardUpdateRequest):
    id: Any = Field(None, alias='_id')

    @validator('id', check_fields=False)
    def ignore_id(cls, value):
        return None

    class Config:
        schema_extra = {
            'example': {
                'amount': '+4',
                'tag': ['zurgo edh', 'turtles'],
                'foil': True,
                'condition': 'NM',
                'signed': False,
                'altered': False,
                'misprint': False,
            }
        }


class CardCreateRequest(CardRequestNoId):
    scryfall_id: UUID
    amount: AmountInt = '+1'
    tag: list[str] = Field(default_factory=list)
    foil: bool = False
    condition: Literal['NM', 'LP', 'MP', 'HP', 'DAMAGED'] = 'NM'
    signed: bool = False
    altered: bool = False
    misprint: bool = False

    def _equals(self, other) -> bool:
        if not isinstance(other, CardCreateRequest):
            return False

        a = self.dict()
        b = other.dict()
        return a == b

    def __eq__(self, other) -> bool:
        return self._equals(other)

    def __ne__(self, other) -> bool:
        return not self._equals(other)

    class Config(CardRequestNoId.Config):
        schema_extra = {
            'example': {
                'scryfall_id': '13f4bafe-0d21-47ba-8f16-0274107d618c',
                'amount': '+1',
                'tag': ['zurgo edh', 'turtles'],
                'foil': True,
                'condition': 'NM',
                'signed': False,
                'altered': False,
                'misprint': False,
            }
        }


class CardUpdateResponse(CustomBaseModel):
    created: list[Card] = Field(default_factory=list)
    updated: list[Card] = Field(default_factory=list)
    deleted: list[Card] = Field(default_factory=list)

    @validator('created', 'updated', 'deleted')
    def remove_duplicates(cls, card_list: list[Card]):
        card_ids = set()
        for card in card_list.copy():
            if card.id in card_ids:
                card_list.remove(card)
            card_ids.add(card.id)
        return card_list

    @staticmethod
    def merge(responses: list['CardUpdateResponse']) -> 'CardUpdateResponse':
        """Create a new single CardUpdateResponse object from a list of CardUpdateResponse objects"""
        return CardUpdateResponse().extend(responses=responses)

    @overload
    def extend(self, *, response: 'CardUpdateResponse') -> 'CardUpdateResponse':
        ...

    @overload
    def extend(self, *, responses: list['CardUpdateResponse']) -> 'CardUpdateResponse':
        ...

    @overload
    def extend(self, *,
               created: list[Card] | None,
               updated: list[Card] | None,
               deleted: list[Card] | None) -> 'CardUpdateResponse':
        ...

    def extend(self, *,
               response: Union['CardUpdateResponse', None] = None,
               responses: Union[list['CardUpdateResponse'], None] = None,
               created: list[Card] | None = None,
               updated: list[Card] | None = None,
               deleted: list[Card] | None = None) -> 'CardUpdateResponse':
        if response:
            if not isinstance(response, CardUpdateResponse):
                raise TypeError(f'Expected CardUpdateResponse, got {type(response)}')
            responses = [response]

        if responses:
            for res in responses:
                self.created.extend(res.created)
                self.updated.extend(res.updated)
                self.deleted.extend(res.deleted)

        if created:
            self.created.extend(created)
        if updated:
            self.updated.extend(updated)
        if deleted:
            self.deleted.extend(deleted)

        return self
