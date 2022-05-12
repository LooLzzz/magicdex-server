from datetime import timedelta

from fastapi import APIRouter, Depends

from .. import models, services

router = APIRouter()
ACCESS_TOKEN_EXPIRE = timedelta(weeks=4)


@router.get('/me', response_model=models.User)
async def read_users_me(current_user: models.User = Depends(services.get_current_user)):
    return current_user


@router.get('/me/items')
async def read_own_items(current_user: models.User = Depends(services.get_current_user)):
    return [{
        'item_id': 'Foo',
        'owner': current_user.username
    }]
