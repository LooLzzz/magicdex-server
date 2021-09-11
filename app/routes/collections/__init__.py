'''
A container for the collections api.

Contains three endpoints accesible by:
    - `collections.CollectionsEndpoint`
    - `collections.CardEndpoint`
    - `collections.AllEndpoint`
'''

from .all import AllEndpoint
from .cards import CardEndpoint
from .collections import CollectionsEndpoint
