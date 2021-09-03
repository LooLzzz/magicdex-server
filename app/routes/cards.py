import re
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .. import mongo
# from ..utils import get_arg_list


class CardsApi(Resource):
    '''
    searchSellers(string q) - use `http://api.scryfall.com/cards/search?q={q}` to fetch cards matching the description and search for users selling them
    '''
    #TODO all this shiz
    pass
