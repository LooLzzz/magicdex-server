import asyncio

from fastapi import HTTPException, status

from .. import cards_collection
from ..models import Card, PyObjectId, User
from ..pagination import Page, PageRequest
from . import users as users_service
from .exceptions import NoneTypeError


async def get_card_owner(card: Card) -> User:
    return await users_service.get_user(card.user_id)


async def get_own_cards_count(user: User) -> int:
    return await cards_collection.count_documents({'user_id': user.id})


async def get_own_cards(user: User, page_request: PageRequest) -> Page[Card]:
    cursor = cards_collection \
        .find({
            'user_id': user.id,
            **page_request.filter
        }) \
        .skip(page_request.offset)
    if page_request.limit:
        cursor = cursor.limit(page_request.limit)

    results, own_cards_count = await asyncio.gather(
        Card.parse_cursor(cursor),
        get_own_cards_count(user)
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
