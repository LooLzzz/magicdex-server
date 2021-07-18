import re
# from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from .. import mongo


class CardsApi(Resource):
    '''
    getInitialPhash() - get initial phash pickle file

    searchSellers(string q) - use `http://api.scryfall.com/cards/search?q={q}` to fetch cards matching the description and search for users selling them
    '''
    pass