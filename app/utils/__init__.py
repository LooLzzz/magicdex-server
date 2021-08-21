# from typing import Union

from .card_condition import CardCondition
from .card_operation import CardOperation


def get_arg_list(parser):
    args = parser.parse_args()
    return list(args.values())

def get_arg_dict(parser):
    return parser.parse_args()

def dictkeys_to_lower(d:dict):
    return { k: v for k,v in d.items() }
