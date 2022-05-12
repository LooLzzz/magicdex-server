import os
import re
from datetime import timedelta

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from .. import users_collection
from ..models.users import Token, User

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


async def get_user(*, id: ObjectId | None = None,
                   username: str | None = None) -> User | None:
    if not any([id, username]):
        return None

    try:
        username = username and re.compile(fr'^{re.escape(username)}$', re.IGNORECASE)
        user = User.parse_obj(
            await users_collection.find_one(
                dict(filter(
                    lambda v: v[1] is not None,
                    [('_id', id), ('username', username)]
                ))
            )
        )

    except Exception as e:
        user = None

    return user


async def authenticate_user(username: str, password: str) -> User | None:
    user = await get_user(username=username)
    if user and user.verify_password(password):
        return user
    return None


async def create_access_token(user: User, expires_delta=timedelta(minutes=15)) -> str:
    token_data = Token(
        sub=str(user.id),
        exp=expires_delta
    )
    return jwt.encode(
        claims=token_data.claims,
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
