import re, json

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

def to_taglist(value):
    if isinstance(value, str):
        value = json.loads(
            value \
                .replace("\\n", '') \
                .replace("\n", '')  \
                .replace("'", '"')  \
                .replace('"{', '{') \
                .replace('}"', '}') \
                .replace('"[', '[') \
                .replace(']"', ']')
        )
    if isinstance(value, list) and all( isinstance(value, str) for value in value ):
        return value
    raise ValueError(f'`tag` field should be an array of strings')

def to_bool(s):
    _s = str(s).lower()
    if _s == 'true':
        return True
    elif _s == 'false':
        return False
    raise BooleanParsingError(f'`{s}` cannot be parsed as boolean')

def to_amount(value):
    if re.match(r'^[+\-][1-9][0-9]*', value): # look for '+X' or '-X'
        return value
    try: # look for 'X'
        return int(value)
    except ValueError:
        raise ValueError(f'`amount` field should be the in form of one of the following: {{X, +X, -X}} where X is an integer')

card_kwargs = {
    '_id':         str,
    'scryfall_id': str,
    'amount':      to_amount,
    'tag':         to_taglist,
    'foil':        to_bool,
    'condition':   CardCondition.parse,
    'signed':      to_bool,
    'altered':     to_bool,
    'misprint':    to_bool
}

def to_card(value) -> dict:
    if isinstance(value, str):
        card = json.loads(
            value \
                .replace("\\n", '') \
                .replace("\n", '')  \
                .replace("'", '"')  \
                .replace('"{', '{') \
                .replace('}"', '}') \
                .replace('"[', '[') \
                .replace(']"', ']')
        )
    else:
        card = value
    
    try:
        if isinstance(value, dict):
            cards = [ dictkeys_to_lower(value) ]
        elif isinstance(value, list):
            cards = [ dictkeys_to_lower(c) for c in value ]
    except:
        raise ValueError(f'`cards` is not a list of dictionaries')

    for card in cards:
        for k,v in card.items():
            if k not in card_kwargs:
                raise ValueError(f'`{k}` is not a valid card field')
            card[k] = card_kwargs[k](v)

    return cards[0] if isinstance(value, dict) else cards
