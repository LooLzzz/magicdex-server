import asyncio

from fastapi import APIRouter, Body, Depends

from .. import pagination as pg
from .. import services
from ..exceptions import HTTPBadRequest, HTTPForbiddenError, HTTPNotFoundError
from ..models import (Card, CardCreateRequest, CardRequestNoId,
                      CardUpdateRequest, CardUpdateResponse, User)

router = APIRouter()


@router.get('/me/{card_id}', response_model=Card)
async def get_own_card(current_user: User = Depends(services.get_current_user),
                       card: Card = Depends(services.get_card_by_id, use_cache=False)):
    await services.allowed_to_view_card(current_user, card, raise_http_error=True)
    return card


@router.get('/me', response_model=pg.generate_response_schema(Card))
async def get_own_cards(current_user: User = Depends(services.get_current_user),
                        pagination: pg.Pagination[Card] = Depends(
                            pg.get_pagination_dependency(offset_kwargs={'default': 0},
                                                         limit_kwargs={'default': 250},
                                                         filter_kwargs={'example': '{"amount": 60}'}))):
    return await pagination.paginate(
        func=services.get_own_cards,
        user=current_user
    )


@router.post('/me/{card_id}', response_model=CardUpdateResponse, include_in_schema=False)
@router.patch('/me/{card_id}', response_model=CardUpdateResponse)
async def update_own_card(card: Card = Depends(services.get_card_by_id, use_cache=False),
                          current_user: User = Depends(services.get_current_user),
                          card_request: CardRequestNoId = Body(None)):
    # authentication #
    await services.allowed_to_view_card(current_user, card, raise_http_error=True)

    if card_request.is_empty():
        raise HTTPBadRequest(
            detail=f'Request body is empty',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # authentication #

    return await services.update_card(
        card.update(
            **card_request.dict(
                exclude_none=True
            )
        )
    )


@router.post('/me', response_model=CardUpdateResponse, include_in_schema=False)
@router.patch('/me', response_model=CardUpdateResponse)
async def update_own_cards(current_user: User = Depends(services.get_current_user),
                           card_requests: list[CardUpdateRequest] = Body(None)):

    # authentication #
    async def verify_edit_permission(card: Card, idx: int):
        try:
            await services.allowed_to_edit_card(current_user, card, raise_http_error=True)
        except HTTPForbiddenError as e:
            raise HTTPForbiddenError(
                detail=e.detail,
                detail_prefix=f'Card[{idx}]:',
            )

    for i, card_req in enumerate(card_requests):
        if not card_req.is_empty():
            raise HTTPBadRequest(
                detail_prefix=f'Card[{i}]:',
                detail='Request is empty',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        if not card_req.id:
            raise HTTPBadRequest(
                detail_prefix=f'Card[{i}]:',
                detail=f"Field 'id' is missing",
                headers={'WWW-Authenticate': 'Bearer'}
            )

    cards = await asyncio.gather(*[
        services.get_card_by_id(card_req.id)
        for card_req in card_requests
    ])

    await asyncio.gather(*[
        verify_edit_permission(card, idx)
        for idx, card in enumerate(cards)
    ])
    # authentication #

    update_results: list[CardUpdateResponse] = await asyncio.gather(*[
        services.update_card(
            card.update(
                **req.dict(
                    exclude_none=True
                )
            )
        )
        for card, req in zip(cards, card_requests)
    ])

    # merge all update results into one
    return CardUpdateResponse.merge(update_results)


@router.put('/me', response_model=CardUpdateResponse)
async def create_own_cards(current_user: User = Depends(services.get_current_user),
                           card_requests: list[CardCreateRequest] = Body(None)):

    # authentication #
    async def verify_uuid_exist(card: Card, idx: int):
        try:
            await services.scryfall.does_uuid_exist(card.scryfall_id, raise_http_error=True)
        except HTTPNotFoundError as e:
            raise HTTPNotFoundError(
                detail=e.detail,
                detail_prefix=f'Card[{idx}]:',
            )

    await asyncio.gather(*[
        verify_uuid_exist(card, idx)
        for idx, card in enumerate(card_requests)
    ])
    # authentication #

    create_results: list[CardUpdateResponse] = await asyncio.gather(*[
        services.create_card(
            Card(
                user_id=current_user.id,
                **req.dict()
            )
        )
        for req in card_requests
    ])

    # merge all create results into one
    return CardUpdateResponse.merge(create_results)


# @router.delete('/me/{card_id}', response_model=Card)
# async def delete_own_card(card: Card = Depends(services.get_card_by_id)):
#     # TODO: delete own card
#     pass

# @router.delete('/me', response_model=list[Card])
# async def delete_own_cards(current_user: User = Depends(services.get_current_user)):
#     # TODO: delete own cards
#     pass
