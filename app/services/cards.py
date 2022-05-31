import asyncio
from typing import Any

from fastapi import Depends, Path

from .. import motor_typing
from .. import pagination as pg
from ..common import cards_collection
from ..exceptions import HTTPBadRequest, HTTPNotFoundError, NoneTypeError
from ..models import (Card, CardCreateRequest, CardUpdateRequest,
                      CardUpdateResponse, PyObjectId, User)
from .utils import compile_case_sensitive_dict

cards_collection: motor_typing.AsyncCollection[Card]


async def get_own_cards_count(user: User, **filter: dict[str, Any]) -> int:
    return await cards_collection.count_documents({
        **filter,
        'user_id': user.id
    })


async def get_own_cards(user: User, page_request: pg.PageRequest) -> pg.PaginatableDict:
    for k in page_request.filter:
        if k not in Card.__alias_fields__:
            raise HTTPBadRequest(
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


async def get_card_by_id(card_id: PyObjectId = Path(None)) -> Card:
    try:
        if not (card_data := await cards_collection.find_one({'_id': card_id})):
            raise NoneTypeError
        return Card.parse_obj(card_data)

    except NoneTypeError:
        raise HTTPNotFoundError(
            detail='Card not found',
            headers={'WWW-Authenticate': 'Bearer'}
        )


async def find_card(card: Card | CardUpdateRequest,
                    user_id: PyObjectId | None = None, *,
                    skip_same_id: bool = False,
                    raise_http_error: bool = True) -> Card | None:
    if user_id is None:
        if not hasattr(card, 'user_id'):
            raise ValueError('user_id is required')
        user_id = card.user_id

    res = await cards_collection.find_one({
        **card.to_mongo(
            exclude={'id', 'date_created', 'amount'}
        ),
        'user_id': user_id
    })

    res = Card.parse_obj(res) if res else None

    if raise_http_error and not res:
        raise HTTPNotFoundError(
            detail='Card not found',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    if (skip_same_id and res
            and res.id == card.id):
        return None
    return res


async def delete_card(card: Card = Depends(get_card_by_id)) -> CardUpdateResponse:
    delete_res = await cards_collection.delete_one(
        filter={'_id': card.id}
    )
    return CardUpdateResponse(deleted=[card])


async def merge_cards(a: Card, b: Card, *, delete_b: bool = True) -> CardUpdateResponse:
    """
    merges `b` into `a`,
    deletes `b` and returns `a|b`
    """
    res = CardUpdateResponse()
    a.update(
        **b.to_mongo(),
        aggregate=True,
        inplace=True
    )
    res.extend(updated=[a])

    if delete_b and a.id != b.id:
        delete_res = await delete_card(b)
        res.extend(response=delete_res)

    return res


async def create_card(create_request: CardCreateRequest, user: User) -> CardUpdateResponse:
    res = CardUpdateResponse()
    new_card = Card(
        **create_request.to_mongo(),
        user_id=user.id
    )

    if prev_card := await find_card(new_card,
                                    raise_http_error=False):
        # card already exists -> update it
        res.extend(
            response=await update_card(
                card=prev_card,
                update_request=CardUpdateRequest(
                    **create_request.to_mongo(),
                    id=prev_card.id
                )
            )
        )

    else:
        # card doesnt exist -> create a new card
        insert_res = await cards_collection.insert_one(
            create_request.to_mongo()
        )
        create_request.id = insert_res.inserted_id
        res.extend(created=[create_request])

    return res


async def update_card(card: Card, update_request: CardUpdateRequest) -> CardUpdateResponse:
    res = CardUpdateResponse()
    new_card = card.update(
        **update_request.to_mongo()
    )

    if prev_card := await find_card(new_card,
                                    skip_same_id=True,
                                    raise_http_error=False):
        res.extend(
            response=await merge_cards(new_card, prev_card)
        )

    update_res = await cards_collection.update_one(
        filter={'_id': new_card.id},
        update={
            '$set': new_card.to_mongo()
        }
    )
    res.extend(updated=[new_card])

    return res
