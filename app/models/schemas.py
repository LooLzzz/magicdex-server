from ..common import crypt_context
from .utils import CustomBaseModel


class UserSchema(CustomBaseModel):
    username: str
    password: str
    public: bool = False

    def generate_password_hash(self) -> str:
        return crypt_context.hash(self.password)
