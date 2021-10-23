'''
A container for the users api.

Contains three endpoints accesible by:
    - `users.UsersEndpoint`
    - `users.CollectionsEndpoint`
    - `users.CardEndpoint`
    - `users.AllEndpoint`
'''

from .users import UsersEndpoint
from .all import AllEndpoint
from .cards import CardEndpoint
from .collections import CollectionsEndpoint
