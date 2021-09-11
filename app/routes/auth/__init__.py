'''
A container for the auth api.

Contains two endpoints accesible by:
    - `auth.UsersEndpoint`
    - `auth.JwtEndpoint`
'''

from .users import UsersEndpoint
from .jwt import JwtEndpoint
