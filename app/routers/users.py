from fastapi import APIRouter, Depends

from .. import models, services

router = APIRouter()


@router.get('/me', response_model=models.User, response_model_exclude={'id'})
async def get_users_me(current_user: models.User = Depends(services.get_current_user)):
    return current_user
