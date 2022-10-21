from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import ValidationError

from . import app, exceptions, routers

app.include_router(routers.auth_router, prefix='/auth', tags=['Auth'])
app.include_router(routers.cards_router, prefix='/cards', tags=['Cards'])
app.include_router(routers.users_router, prefix='/users', tags=['Users'])


@app.get('/', include_in_schema=False)
async def redirect_docs():
    return RedirectResponse(
        url=app.docs_url,
        status_code=status.HTTP_308_PERMANENT_REDIRECT
    )


@app.post('/token', include_in_schema=False)
async def redirect_login():
    return RedirectResponse(
        url='/auth/login',
        status_code=status.HTTP_308_PERMANENT_REDIRECT
    )


@app.exception_handler(404)
async def nop(request: Request, exc: HTTPException):
    if isinstance(exc, exceptions.HTTPNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                'detail': exc.detail
            }
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            'detail': 'This is not the page you are looking for',
            'docs': str(request.base_url) + app.docs_url.lstrip('/')
        }
    )


@app.exception_handler(ValidationError)
async def nop(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'detail': exc.errors()
        }
    )
