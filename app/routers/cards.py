import asyncio

from fastapi import APIRouter, Body, Depends

from .. import pagination as pg
from .. import services
from ..exceptions import HTTPBadRequest, HTTPForbiddenError, HTTPNotFoundError
from ..models import (Card, CardCreateRequest, CardDeleteRequest,
                      CardUpdateRequest, CardUpdateRequestNoId,
                      CardUpdateResponse, User)

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
                          card_request: CardUpdateRequestNoId = Body(None)):
    # authentication #
    await services.allowed_to_edit_card(current_user, card, raise_http_error=True)

    if card_request.is_empty():
        raise HTTPBadRequest(
            detail=f'Request body is empty',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    # authentication #

    return await services.update_card(
        card=card,
        update_request=card_request
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

    # merge all update results into one
    return CardUpdateResponse.merge(
        await asyncio.gather(*[
            services.update_card(card=card,
                                 update_request=req)
            for card, req in zip(cards, card_requests)
        ])
    )


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

    # check for duplicates
    cards = []
    for idx, card in enumerate(card_requests):
        if card in cards:
            raise HTTPBadRequest(
                detail_prefix=f'Card[{idx}]:',
                detail=f'Duplicated request',
            )
        cards.append(card)
    # authentication #

    # merge all create results into one
    return CardUpdateResponse.merge(
        await asyncio.gather(*[
            services.create_card(
                create_request=req,
                user=current_user
            )
            for req in card_requests
        ])
    )


@router.delete('/me/{card_id}', response_model=CardUpdateResponse)
async def delete_own_card(current_user: User = Depends(services.get_current_user),
                          card: Card = Depends(services.get_card_by_id)):
    # authentication #
    await services.allowed_to_edit_card(current_user, card, raise_http_error=True)
    # authentication #

    return await services.delete_card(card)


@router.delete('/me', response_model=CardUpdateResponse)
async def delete_own_cards(current_user: User = Depends(services.get_current_user),
                           card_requests: list[CardDeleteRequest] = Body(None)):
    # authentication #
    async def verify_edit_permission(card: Card, idx: int):
        try:
            await services.allowed_to_edit_card(current_user, card, raise_http_error=True)
        except HTTPForbiddenError as e:
            raise HTTPForbiddenError(
                detail=e.detail,
                detail_prefix=f'Card[{idx}]:',
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

    # merge all delete results into one
    return CardUpdateResponse.merge(
        await asyncio.gather(*[
            services.delete_card(card)
            for card in cards
        ]))
