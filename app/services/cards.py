import asyncio
from typing import Any

from fastapi import Depends, Path

from .. import motor_typing
from .. import pagination as pg
from ..common import cards_collection
from ..exceptions import HTTPBadRequest, HTTPNotFoundError, NoneTypeError
from ..models import Card, CardUpdateResponse, PyObjectId, User
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


async def find_card(card: Card, raise_http_error: bool = True) -> Card | None:
    res = await cards_collection.find_one(
        card.to_mongo(
            exclude={'id', 'date_created', 'amount'}
        )
    )
    if not res and raise_http_error:
        raise HTTPNotFoundError(
            detail='Card not found',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return Card.parse_obj(res) if res else None


async def create_card(new_card: Card) -> CardUpdateResponse:
    res = CardUpdateResponse()

    if (old_card := await find_card(new_card, raise_http_error=False)):
        # card already exists -> update it
        res.extend(
            responses=[
                await merge_cards(old_card, new_card, delete_b=False),
                await update_card(old_card)
            ]
        )

    else:
        # card doesnt exist -> create a new card
        insert_res = await cards_collection.insert_one(
            new_card.to_mongo()
        )
        new_card.id = insert_res.inserted_id
        res.extend(created=[new_card])

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
        **b.to_mongo(
            exclude_none=True
        ),
        aggregate=True,
        inplace=True
    )
    res.extend(updated=[a])

    if delete_b:
        delete_res = await delete_card(b)
        res.extend(response=delete_res)

    return res


async def update_card(new_card: Card) -> CardUpdateResponse:
    res = CardUpdateResponse()

    if (old_card := await find_card(new_card, raise_http_error=False)):
        # merge and delete `prev_card`
        res.extend(
            response=await merge_cards(new_card, old_card)
        )

    update_res = await cards_collection.update_one(
        filter={'_id': new_card.id},
        update={
            '$set': new_card.to_mongo()
        }
    )
    res.extend(updated=[new_card])

    return res
