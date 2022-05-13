from fastapi import APIRouter, Depends, HTTPException, status

from .. import models, services

router = APIRouter()


@router.get('/me', response_model=list[models.Card])
async def get_own_cards(current_user: models.User = Depends(services.get_current_user)):
    return await services.get_own_cards(current_user)


@router.get('/me/{card_id}', response_model=models.Card)
async def get_own_card(current_user: models.User = Depends(services.get_current_user),
                       card: models.Card = Depends(services.get_card_by_id)):
    if card.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not allowed to access this card',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return card


@router.post('/me', response_model=list[models.Card])
async def update_own_cards(current_user: models.User = Depends(services.get_current_user)):
    # TODO: update own cards
    pass


@router.post('/me/{card_id}', response_model=models.Card)
async def update_own_card(current_user: models.User = Depends(services.get_current_user),
                          card: models.Card = Depends(services.get_card_by_id)):
    # TODO: update own card
    pass


@router.put('/me', response_model=list[models.Card])
async def create_own_cards(current_user: models.User = Depends(services.get_current_user)):
    # TODO: create own cards
    pass


@router.put('/me/{card_id}', response_model=models.Card)
async def create_own_card(card: models.Card = Depends(services.get_card_by_id)):
    # TODO: create own card
    pass
