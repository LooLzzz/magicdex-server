from flask import redirect
from flask_restful import Resource

# from ...utils import get_arg_dict, get_arg_list


class PhashEndpoint(Resource):
    '''
    ## `/cards/phash` ENDPOINT

    ### GET
    Retrieves an initial phash pickle file
    '''
    def get(self):
        return redirect('https://github.com/LooLzzz/magicdex-server/raw/phash/image_data.pickle', 308)
