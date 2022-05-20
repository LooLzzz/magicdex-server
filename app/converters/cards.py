from fastapi import HTTPException, status

from .. import services
from ..models import Card, CardRequest


async def convert_card_in(card_in: CardRequest) -> Card:
    kwargs = card_in.dict(exclude_none=True, exclude_unset=True)
    _id = kwargs.pop('id')

    if not kwargs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Card is empty',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    card = await services.get_card_by_id(_id)
    for k, v in kwargs.items():
        setattr(card, k, v)
    return card
