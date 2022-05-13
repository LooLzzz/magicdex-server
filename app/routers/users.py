from fastapi import APIRouter, Depends

from .. import services
from ..models import User

router = APIRouter()


@router.get('/me', response_model=User, response_model_exclude={'id'})
async def get_users_me(current_user: User = Depends(services.get_current_user)):
    return current_user
