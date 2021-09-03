import json
# from typing import Union, List, Dict

from .errors import BooleanParsingError


def get_arg_list(parser):
    args = get_arg_dict(parser)
    return list(args.values())

def get_arg_dict(parser):
    res = parser.parse_args()
    res = dictkeys_to_lower(res)
    res = str(res) \
            .replace("\\n", '') \
            .replace("\n", '')  \
            .replace("'", '"')  \
            .replace('"{', '{') \
            .replace('}"', '}') \
            .replace('"[', '[') \
            .replace(']"', ']')
    res = json.loads(res)
    for k,v in res.items():
        try:
            res[k] = to_bool(v)
        except BooleanParsingError as e:
            pass
    return res

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
