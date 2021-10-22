'''
A container for the users api.

Contains three endpoints accesible by:
    - `users.CollectionsEndpoint`
    - `users.CardEndpoint`
    - `users.AllEndpoint`
'''

from .all import AllEndpoint
from .cards import CardEndpoint
from .collections import CollectionsEndpoint
