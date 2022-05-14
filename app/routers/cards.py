from fastapi import APIRouter, Depends, HTTPException, Request, status

from .. import pagination as pg
from .. import services
from ..models import Card, User

router = APIRouter()


@router.get('/me', response_model=pg.generate_response_schema(Card))
async def get_own_cards(request: Request,
                        current_user: User = Depends(services.get_current_user),
                        pagination: pg.Pagination[Card] = Depends(
                            pg.get_pagination_parser(offset_kwargs={'default': 0},
                                                     limit_kwargs={'default': 250},
                                                     filter_kwargs={'example': '{"name": "fireball"}'})
                        )):
    pagination = await pagination.paginate(
        endpoint_url=request.url_for('get_own_cards'),
        func=services.get_own_cards,
        user=current_user
    )
    return pagination.response


@router.get('/me/{card_id}', response_model=Card)
async def get_own_card(current_user: User = Depends(services.get_current_user),
                       card: Card = Depends(services.get_card_by_id)):
    if card.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not allowed to access this card',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return card


@router.post('/me', response_model=list[Card])
async def update_own_cards(current_user: User = Depends(services.get_current_user)):
    # TODO: update own cards
    pass


@router.post('/me/{card_id}', response_model=Card)
async def update_own_card(current_user: User = Depends(services.get_current_user),
                          card: Card = Depends(services.get_card_by_id)):
    # TODO: update own card
    pass


@router.put('/me', response_model=list[Card])
async def create_own_cards(current_user: User = Depends(services.get_current_user)):
    # TODO: create own cards
    pass


@router.put('/me/{card_id}', response_model=Card)
async def create_own_card(card: Card = Depends(services.get_card_by_id)):
    # TODO: create own card
    pass


@router.delete('/me', response_model=list[Card])
async def delete_own_cards(current_user: User = Depends(services.get_current_user)):
    # TODO: delete own cards
    pass


@router.delete('/me/{card_id}', response_model=Card)
async def delete_own_card(card: Card = Depends(services.get_card_by_id)):
    # TODO: delete own card
    pass
