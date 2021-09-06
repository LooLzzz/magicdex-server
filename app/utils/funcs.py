import re, json
# from typing import Union, List, Dict

from .errors import BooleanParsingError


def get_arg_list(parser):
    args = get_arg_dict(parser)
    return list(args.values())

def get_arg_dict(parser):
    kwargs = parser.parse_args()
    return dictkeys_to_lower(kwargs)

def to_json(value):
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

def dictkeys_to_lower(d:dict):
    return { k: v for k,v in d.items() }

def to_bool(s):
    _s = str(s).lower()
    if _s == 'true':
        return True
    elif _s == 'false':
        return False
    else:
        raise BooleanParsingError(f'`{s}` cannot be parsed as boolean')

def to_amount(value:str):
    if re.match(r'^[+\-][1-9][0-9]*', value): # look for '+X' or '-X'
        return value
    try: # look for 'X'
        return int(value)
    except ValueError:
        raise ValueError(f'this field should be the in form of one of the following: {{X, +X, -X}} where X is an integer')
