from fastapi import HTTPException, status


class NoneTypeError(TypeError):
    """Raised when a NoneType is encountered"""


class HTTPForbiddenError(HTTPException):
    def __init__(self,
                 detail='You are not allowed to access this resource',
                 status_code=status.HTTP_403_FORBIDDEN,
                 headers={'WWW-Authenticate': 'Bearer'},
                 *args, **kwargs):
        super().__init__(
            detail=detail,
            status_code=status_code,
            headers=headers,
            *args, **kwargs
        )


class HTTPNotFoundError(HTTPException):
    def __init__(self,
                 detail='Resource not found',
                 status_code=status.HTTP_404_NOT_FOUND,
                 *args, **kwargs):
        super().__init__(
            detail=detail,
            status_code=status_code,
            *args, **kwargs
        )


class HTTPBadRequest(HTTPException):
    def __init__(self,
                 detail='Request is empty',
                 status_code=status.HTTP_400_BAD_REQUEST,
                 *args, **kwargs):
        super().__init__(
            detail=detail,
            status_code=status_code,
            *args, **kwargs
        )
