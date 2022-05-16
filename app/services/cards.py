import asyncio
from typing import Any

from fastapi import HTTPException, status

from .. import pagination as pg
from ..common import cards_collection
from ..exceptions import NoneTypeError
from ..models import Card, PyObjectId, User
from . import users as users_service
from .utils import compile_case_sensitive_dict


async def get_card_owner(card: Card) -> User:
    return await users_service.get_user(card.user_id)


async def get_own_cards_count(user: User, **filter: dict[str, Any]) -> int:
    return await cards_collection.count_documents({
        **filter,
        'user_id': user.id
    })


async def get_own_cards(user: User, page_request: pg.PageRequest) -> pg.PaginatableDict:
    for k in page_request.filter:
        if k not in Card.__alias_fields__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Filter field ({k!r}) not in {Card.__name__!r} model',
                headers={'WWW-Authenticate': 'Bearer'}
            )

    filter = compile_case_sensitive_dict(page_request.filter,
                                         ignorecase=True,
                                         match_whole_word=False)

    results, own_cards_count = await asyncio.gather(
        Card.parse_cursor(
            cards_collection
            .find({
                **filter,
                'user_id': user.id,
            })
            .skip(page_request.offset)
            .limit(page_request.limit or 0)
        ),
        get_own_cards_count(user, **filter)
    )

    return {
        'results': results,
        'total_items': own_cards_count
    }


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
