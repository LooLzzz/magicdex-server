from datetime import datetime
from typing import Literal
from uuid import UUID

from motor import core as motor_core

from .utils import MongoBaseModel, PyObjectId

ConditionT = Literal['NM', 'LP', 'MP', 'HP', 'DAMAGED']


class Card(MongoBaseModel):
    user_id: PyObjectId
    scryfall_id: UUID
    amount: int
    tag: list[str]
    foil: bool
    condition: ConditionT
    signed: bool
    altered: bool
    misprint: bool
    date_created: datetime

    @classmethod
    async def parse_cursor(cls, cursor: motor_core.Cursor['Card']) -> list['Card']:
        return [cls.parse_obj(card_data)
                async for card_data in cursor
                if card_data]
