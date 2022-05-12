import os
from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

from app import users_collection

from ..models.users import Token, User


async def get_user(*, id: ObjectId | None = None,
                   username: str | None = None) -> User | None:
    if not any([id, username]):
        return None
    user = None

    try:
        user = User.parse_obj(
            await users_collection.find_one(
                dict(filter(
                    lambda v: v[1] is not None,
                    [('_id', id), ('username', username)]
                ))
            )
        )

    except Exception as e:
        """skip"""

    return user


async def authenticate_user(username: str, password: str) -> User | None:
    user = await get_user(username=username)
    if user and user.verify_password(password):
        return user
    return None


def create_access_token(user: User, expires_delta=timedelta(minutes=15)) -> str:
    return jwt.encode(
        {'user_id': str(user.id),
         'exp': datetime.utcnow() + expires_delta},
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        token_data = Token.parse_obj(
            jwt.decode(
                token,
                key=SECRET_KEY,
                algorithms=[ALGORITHM]
            )
        )

    except:
        raise credentials_exception

    user = await get_user(id=token_data.user_id)
    if not user:
        raise credentials_exception
    return user
