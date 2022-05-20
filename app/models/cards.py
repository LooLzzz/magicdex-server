from datetime import datetime
from typing import Any, Literal, Union, overload
from uuid import UUID

from pydantic import Field, PositiveInt, validator
from pymongo.results import DeleteResult, UpdateResult

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
    date_created: datetime

    def update(self, aggregate: bool = False, inplace: bool = False, **kwargs) -> 'Card':
        if inplace:
            match kwargs:
                case {'amount': amount} if AmountInt.is_relative(amount) or aggregate:
                    self.amount += amount
                case {'amount': amount}:
                    self.amount = amount
                case {'tag': tag}:
                    self.tag = tag
                case {'foil': foil}:
                    self.foil = foil
                case {'condition': condition}:
                    self.condition = condition
                case {'signed': signed}:
                    self.signed = signed
                case {'altered': altered}:
                    self.altered = altered
                case {'misprint': misprint}:
                    self.misprint = misprint
                case {'date_created': date_created}:
                    self.date_created = date_created
            return self

        else:
            res = super().copy(update=kwargs)
            match kwargs:
                case {'amount': amount} if AmountInt.is_relative(amount) or aggregate:
                    res.amount += self.amount
            return res

    def to_mongo(self,
                 by_alias: bool = True,
                 exclude: set | None = {'id'},
                 exclude_none: bool = True,
                 **kwargs) -> dict:
        res = self.dict(by_alias=by_alias,
                        exclude=exclude,
                        exclude_none=exclude_none,
                        **kwargs)
        res.update({
            'scryfall_id': str(self.scryfall_id),
        })
        return res


class CardRequest(CustomBaseModel):
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
                'amount': '+4',
                'tag': ['zurgo edh', 'turtles'],
                'foil': True,
                'condition': 'NM',
                'signed': False,
                'altered': False,
                'misprint': False,
            }
        }


class CardRequestNoId(CardRequest):
    id: Any = Field(None, alias='_id')

    @validator('id', check_fields=False)
    def ignore_id(cls, value):
        return None


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

    @overload
    def extend(self, *, response: 'CardUpdateResponse') -> 'CardUpdateResponse':
        ...

    @overload
    def extend(self, *,
               created: list[Card] | None,
               updated: list[Card] | None,
               deleted: list[Card] | None) -> 'CardUpdateResponse':
        ...

    def extend(self, *,
               response: Union['CardUpdateResponse', None] = None,
               created: list[Card] | None = None,
               updated: list[Card] | None = None,
               deleted: list[Card] | None = None) -> 'CardUpdateResponse':
        if response:
            self.created.extend(response.created)
            self.updated.extend(response.updated)
            self.deleted.extend(response.deleted)
        if created:
            self.created.extend(created)
        if updated:
            self.updated.extend(updated)
        if deleted:
            self.deleted.extend(deleted)
        return self

    class Config:
        validate_assignment = True
