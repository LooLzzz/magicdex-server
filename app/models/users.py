from datetime import datetime, timedelta
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

from ..common import crypt_context
from .utils import MongoBaseModel, PyObjectId


class Token(BaseModel):
    subject: PyObjectId = Field(alias='sub')
    expires_at: timedelta | datetime = Field(alias='exp')
    issued_at: datetime = Field(default_factory=datetime.utcnow, alias='iat')
    jwt_id: UUID = Field(default_factory=uuid4, alias='jti')

    @validator('expires_at')
    def expires_at_to_datetime(cls, value: timedelta | datetime) -> datetime:
        if isinstance(value, timedelta):
            value += datetime.utcnow()
        return value

    @property
    def user_id(self) -> PyObjectId:
        return self.subject

    @property
    def claims(self) -> dict:
        res = self.dict(by_alias=True)
        res.update({
            'sub': str(res['sub']),
            'jti': str(res['jti'])
        })
        return res

    class Config:
        allow_population_by_field_name = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class User(MongoBaseModel):
    username: str
    hashed_password: str = Field(alias='password')
    public: bool = False
    date_created: datetime = Field(default_factory=datetime.utcnow)

    def verify_password(self, password: str) -> bool:
        return crypt_context.verify(password, self.hashed_password)

