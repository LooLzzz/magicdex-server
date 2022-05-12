from datetime import datetime
from typing import Literal
from uuid import UUID

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
