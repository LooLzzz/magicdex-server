import asyncio
from typing import Any

from fastapi import HTTPException, status

from .. import cards_collection
from ..models import Card, PyObjectId, User
from ..pagination import Page, PageRequest
from . import users as users_service
from .exceptions import NoneTypeError
from .utils import compile_case_sensitive_dict


async def get_card_owner(card: Card) -> User:
    return await users_service.get_user(card.user_id)


async def get_own_cards_count(user: User, filter: dict[str, Any] = None) -> int:
    return await cards_collection.count_documents({
        **(filter or {}),
        'user_id': user.id
    })


async def get_own_cards(user: User, page_request: PageRequest) -> Page[Card]:
    for k in page_request.filter:
        if k not in Card.__alias_fields__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid filter',
                headers={'WWW-Authenticate': 'Bearer'}
            )

    cursor = cards_collection \
        .find({
            **compile_case_sensitive_dict(page_request.filter,
                                          match_whole_word=False),
            'user_id': user.id,
        }) \
        .skip(page_request.offset)
    if page_request.limit:
        cursor = cursor.limit(page_request.limit)

    results, own_cards_count = await asyncio.gather(
        Card.parse_cursor(cursor),
        get_own_cards_count(user, filter=page_request.filter)
    )

    return Page(
        request=page_request,
        results=results,
        total_items=own_cards_count
    )


async def get_card_by_id(card_id: PyObjectId) -> Card:
    try:
        if not (card_data := await cards_collection.find_one({'_id': card_id})):
            raise NoneTypeError
        return Card.parse_obj(card_data)

    except NoneTypeError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Card not found',
            headers={'WWW-Authenticate': 'Bearer'}
        )
