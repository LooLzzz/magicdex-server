from datetime import datetime

from passlib.context import CryptContext
from pydantic import BaseModel, Field

from .utils import MongoBaseModel, PyObjectId

crypt_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto'
)


class Token(BaseModel):
    user_id: PyObjectId | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class User(MongoBaseModel):
    username: str
    hashed_password: str | None = Field(None, alias='password', exclude=True)
    public: bool | None = None
    date_created: datetime | None = None

    def verify_password(self, password: str) -> bool:
        return crypt_context.verify(password, self.hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return crypt_context.hash(password)
