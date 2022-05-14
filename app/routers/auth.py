from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from .. import services
from ..models import TokenResponse, User

router = APIRouter()
ACCESS_TOKEN_EXPIRE = timedelta(weeks=4)


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl='/auth/login',
    scheme_name='Bearer'
)


@router.post('', response_model=TokenResponse)
@router.get('', response_model=TokenResponse, include_in_schema=False)
@router.post('/login', response_model=TokenResponse, include_in_schema=False)
@router.get('/login', response_model=TokenResponse, include_in_schema=False)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await services.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return await services.create_access_token(
        user=user,
        expires_delta=ACCESS_TOKEN_EXPIRE
    )


@router.put('', response_model=TokenResponse)
@router.put('/register', response_model=TokenResponse, include_in_schema=False)
async def register(form_data: User):
    user = await services.create_user(form_data)

    return await services.create_access_token(
        user=user,
        expires_delta=ACCESS_TOKEN_EXPIRE
    )
