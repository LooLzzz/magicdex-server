from fastapi import HTTPException, status


class NoneTypeError(TypeError):
    """Raised when a NoneType is encountered"""


class HTTPForbiddenError(HTTPException):
    def __init__(self,
                 detail: str = 'You are not allowed to access this resource',
                 detail_prefix: str | None = None,
                 status_code: int = status.HTTP_403_FORBIDDEN,
                 headers: dict = {'WWW-Authenticate': 'Bearer'},
                 *args, **kwargs):
        detail_prefix = f'{detail_prefix.rstrip()} ' if detail_prefix else ''
        super().__init__(
            detail=f'{detail_prefix}{detail}',
            status_code=status_code,
            headers=headers,
            *args, **kwargs
        )


class HTTPNotFoundError(HTTPException):
    def __init__(self,
                 detail: str = 'Resource not found',
                 detail_prefix: str | None = None,
                 status_code: int = status.HTTP_404_NOT_FOUND,
                 *args, **kwargs):
        detail_prefix = f'{detail_prefix.rstrip()} ' if detail_prefix else ''
        super().__init__(
            detail=f'{detail_prefix}{detail}',
            status_code=status_code,
            *args, **kwargs
        )


class HTTPBadRequest(HTTPException):
    def __init__(self,
                 detail: str,
                 detail_prefix: str | None = None,
                 status_code: int = status.HTTP_400_BAD_REQUEST,
                 *args, **kwargs):
        detail_prefix = f'{detail_prefix.rstrip()} ' if detail_prefix else ''
        super().__init__(
            detail=f'{detail_prefix}{detail}',
            status_code=status_code,
            *args, **kwargs
        )
