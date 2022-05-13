from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

from . import app, routers

app.include_router(routers.auth_router, prefix='/auth', tags=['auth'])
app.include_router(routers.cards_router, prefix='/cards', tags=['cards'])
app.include_router(routers.users_router, prefix='/users', tags=['users'])


@app.get('/', include_in_schema=False)
async def nop():
    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        detail='This is not the web page you are looking for'
    )


@app.post('/token', include_in_schema=False)
async def redirect_login():
    return RedirectResponse(
        url='/auth/login',
        status_code=status.HTTP_308_PERMANENT_REDIRECT
    )
