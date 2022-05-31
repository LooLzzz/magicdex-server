from datetime import timedelta
from typing import TypedDict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pymongo.results import InsertOneResult

from .. import motor_typing
from ..common import ALGORITHM, SECRET_KEY, users_collection
from ..exceptions import HTTPForbiddenError
from ..models import Card, PyObjectId, Token, User, UserSchema
from ..utils import filter_dict_values
from .utils import compile_case_sensitive_str

users_collection: motor_typing.AsyncCollection[User]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
AccessTokenDict = TypedDict('AccessTokenT', {'access_token': str, 'token_type': str})


async def allowed_to_view_card(user: User, card: Card, *, raise_http_error: bool = True) -> bool:
    if (user.public
            or card.user_id == user.id):
        return True

    if raise_http_error:
        raise HTTPForbiddenError('You are not allowed to view this resource')

    return False


async def allowed_to_edit_card(user: User, card: Card, *, raise_http_error: bool = True) -> bool:
    if card.user_id == user.id:
        return True

    if raise_http_error:
        raise HTTPForbiddenError('You are not allowed to edit this resource')

    return False


async def get_user(*, id: PyObjectId | None = None,
                   username: str | None = None) -> User | None:
    if not any([id, username]):
        return None

    try:
        username = username and compile_case_sensitive_str(username,
                                                           match_whole_word=True)
        user = User.parse_obj(
            await users_collection.find_one(
                filter_dict_values({
                    '_id': id,
                    'username': username
                })
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


async def create_access_token(user: User, expires_delta=timedelta(minutes=15)) -> AccessTokenDict:
    return {
        'token_type': 'bearer',
        'access_token': jwt.encode(key=SECRET_KEY,
                                   algorithm=ALGORITHM,
                                   claims=Token(sub=str(user.id),
                                                exp=expires_delta).claims)
    }


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


async def insert_user_to_db(user: User) -> User:
    try:
        insert_result = await users_collection.insert_one(
            user.dict(by_alias=True)
        )

        user.id = insert_result.inserted_id
        return user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error while inserting new user {e!r}'
        )


async def create_user(form_data: UserSchema) -> User:
    if await get_user(username=form_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User already exists'
        )

    return await insert_user_to_db(
        User(username=form_data.username,
             hashed_password=form_data.generate_password_hash())
    )
