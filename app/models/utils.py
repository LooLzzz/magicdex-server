from typing import TypeVar

from bson import ObjectId
from motor import core as motor_core
from pydantic import BaseModel, Field

_DocType = TypeVar('_DocType', bound=BaseModel)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError('Invalid objectid')
        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update({
            'type': 'string',
        })


class CustomBaseModel(BaseModel):
    @classmethod
    @property
    def __alias_fields__(cls) -> list[str]:
        return [field.alias for field in cls.__fields__.values()]

    def is_empty(self) -> bool:
        return not any(
            self.dict(exclude_none=True)
        )

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str,
                         PyObjectId: str}


class MongoModel(CustomBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    @classmethod
    async def parse_cursor(cls, cursor: motor_core.Cursor[_DocType]) -> list[_DocType]:
        return [cls.parse_obj(card_data)
                async for card_data in cursor
                if card_data]

    class Config(CustomBaseModel.Config):
        extra = 'forbid'
        arbitrary_types_allowed = True


class AmountInt(int):
    """
    Accepts int or string-like int (`'+1'`, `...`).

    If string and starts with `+` or `-`, it's considered a relative amount. (`cls.RelativeInt`)

    Otherwise, it's considered an absolute amount. (`cls.AbsoluteInt`)
    """
    class RelativeInt(int):
        def is_relative(self) -> bool:
            return True

    class AbsoluteInt(int):
        def is_relative(self) -> bool:
            return False

    @classmethod
    def is_relative(cls, value) -> bool:
        if isinstance(value, cls.RelativeInt):
            return True
        return False

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        match value:
            case str() if value.startswith('+') or value.startswith('-'):
                return cls.RelativeInt(value)

            case int() if value < 0:
                return cls.RelativeInt(value)

            case str() | int():
                return cls.AbsoluteInt(value)

            case _:
                raise TypeError(f'{value} is not an int or strInt')

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update({
            'type': 'integer'
        })
