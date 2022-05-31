from typing import Type, TypeVar, Union
from uuid import UUID

from bson import ObjectId
from motor import core as motor_core
from pydantic import BaseModel, Field, validate_model

DocType = TypeVar('DocType', bound=BaseModel)
ModelType = TypeVar('ModelType', bound=BaseModel)


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

    def check(self):
        values, fields_set, validation_error = validate_model(model=self.__class__,
                                                              input_data=self.__dict__)
        if validation_error:
            raise validation_error
        try:
            object.__setattr__(self, '__dict__', values)
        except TypeError as e:
            raise TypeError(
                'Model values must be a dict; You may not have returned '
                'a dictionary from a root validator'
            ) from e
        object.__setattr__(self, '__fields_set__', fields_set)

    def is_empty(self) -> bool:
        return not self.dict(
            exclude_none=True,
            exclude={'id'}
        )

    def to_mongo(self,
                 by_alias: bool = True,
                 exclude: set | None = {'id'},
                 exclude_none: bool = True,
                 **kwargs) -> dict:
        res = self.dict(by_alias=by_alias,
                        exclude=exclude,
                        exclude_none=exclude_none,
                        **kwargs)

        return {
            k: str(v) if isinstance(v, UUID) else v
            for k, v in res.items()
        }

    @classmethod
    def parse_obj(cls: Type[ModelType], obj: dict | BaseModel) -> ModelType:
        if isinstance(obj, BaseModel):
            obj = obj.dict()
        return super().parse_obj(obj)

    class Config:
        validate_assignment = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str,
                         PyObjectId: str}


class MongoModel(CustomBaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')

    @classmethod
    async def parse_cursor(cls, cursor: motor_core.Cursor[DocType]) -> list[DocType]:
        return [cls.parse_obj(card_data)
                async for card_data in cursor
                if card_data]

    class Config(CustomBaseModel.Config):
        extra = 'forbid'
        arbitrary_types_allowed = True


class AmountInt(int):
    def __init__(self, value, is_relative: bool | None = None):
        self._value = value
        self._is_relative = is_relative

        if self._is_relative is None:
            self._parse_is_relative_value()

    def is_relative(self) -> bool:
        return self._is_relative

    def is_absolute(self) -> bool:
        return not self._is_relative

    def _parse_is_relative_value(self):
        try:
            value = self._value
            self._value = int(value)
            match value:
                case AmountInt():
                    self._is_relative = value._is_relative

                case str() if (value.startswith('+') or value.startswith('-')) and value[1:].isdecimal():
                    self._is_relative = True

                case int() if value < 0:
                    self._is_relative = True

                case int():
                    self._is_relative = False

                case str() if value.isdecimal():
                    self._is_relative = False

                case _:
                    self._is_relative = False

        except Exception:
            raise TypeError(f'{value} is not an int or StrInt')

    def __add__(self, other) -> Union['AmountInt', int]:

        match other:
            case AmountInt() if self._is_relative and other._is_relative:
                value = self._value + other._value
                return AmountInt(f'+{value}' if value >= 0 else value)

            case AmountInt():
                return self._value + other._value

            case _:
                return self._value + other

    def __repr__(self) -> str:
        if self._is_relative:
            return f'+{self._value}' if self._value >= 0 else f'{self._value}'
        return repr(self._value)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return cls(value)
