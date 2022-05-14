from fastapi import APIRouter, Depends

from .. import services
from ..models import User

router = APIRouter()
response_model_exclude = {'id', 'hashed_password', 'password'}


@router.post('/me', response_model=User, response_model_exclude=response_model_exclude, include_in_schema=False)
@router.get('/me', response_model=User, response_model_exclude=response_model_exclude)
async def get_users_me(current_user: User = Depends(services.get_current_user)):
    return current_user
