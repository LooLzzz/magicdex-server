from pydantic import BaseModel

from ..common import crypt_context


class UserSchema(BaseModel):
    username: str
    password: str
    public: bool = False

    def generate_password_hash(self) -> str:
        return crypt_context.hash(self.password)
