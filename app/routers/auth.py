from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .. import models, services

router = APIRouter()
ACCESS_TOKEN_EXPIRE = timedelta(weeks=4)


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    scheme_name='Bearer'
)


@router.post('/login', response_model=models.TokenResponse)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user: models.User = await services.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = await services.create_access_token(
        user=user,
        expires_delta=ACCESS_TOKEN_EXPIRE
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }
