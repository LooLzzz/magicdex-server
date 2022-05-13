from fastapi import HTTPException, status

from .. import cards_collection
from ..models import Card, PyObjectId, User
from .exceptions import NoneTypeError
from .users import get_user


async def get_card_owner(card: Card) -> User:
    return await get_user(card.user_id)


async def get_own_cards(user: User) -> list[Card]:
    return [Card.parse_obj(card)
            async for card in cards_collection.find({'user_id': user.id})]


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
