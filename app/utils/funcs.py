import re, json
from typing import Union, List, Dict

from .errors import BooleanParsingError
from .enums import CardCondition


def get_arg_list(parser):
    args = get_arg_dict(parser)
    return list(args.values())

def get_arg_dict(parser):
    kwargs = parser.parse_args()
    return dictkeys_to_lower(kwargs)

def dictkeys_to_lower(d:dict):
    return { k: v for k,v in d.items() }

def to_json(value) -> Union[dict, List[dict]]:
    if isinstance(value, (dict, list)):
        return value
    return json.loads(
        value \
            .replace("\\n", '') \
            .replace("\n", '')  \
            .replace("'", '"')  \
            .replace('"{', '{') \
            .replace('}"', '}') \
            .replace('"[', '[') \
            .replace(']"', ']')
    )

def to_bool(s):
    _s = str(s).lower()
    if _s == 'true':
        return True
    elif _s == 'false':
        return False
    else:
        raise BooleanParsingError(f'`{s}` cannot be parsed as boolean')

def to_amount(value):
    if re.match(r'^[+\-][1-9][0-9]*', value): # look for '+X' or '-X'
        return value
    try: # look for 'X'
        return int(value)
    except ValueError:
        raise ValueError(f'`amount` field should be the in form of one of the following: {{X, +X, -X}} where X is an integer')

def to_card_list(value) -> List[dict]:
    cards = json.loads(
        value \
            .replace("\\n", '') \
            .replace("\n", '')  \
            .replace("'", '"')  \
            .replace('"{', '{') \
            .replace('}"', '}') \
            .replace('"[', '[') \
            .replace(']"', ']')
    )

    if not isinstance(cards, list):
        raise ValueError(f'`cards` is not a list')
    try:
        cards = [ dictkeys_to_lower(card) for card in cards ]
    except:
        raise ValueError(f'`cards` is not a list of dictionaries')

    card_kwargs = {
        'scryfall_id': str,
        'amount':      to_amount,
        'tag':         to_json,
        'foil':        to_bool,
        'condition':   CardCondition.parse,
        'signed':      to_bool,
        'altered':     to_bool,
        'misprint':    to_bool
    }

    for card in cards:
        for k,v in card.items():
            if k not in card_kwargs:
                raise ValueError(f'`{k}` is not a valid card field')
            card[k] = card_kwargs[k](v)

    return cards
