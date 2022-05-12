from .. import cards_collection
from ..models import Card, User
from .users import get_user


def get_card_owner(card: Card) -> User:
    return get_user(card.user_id)
