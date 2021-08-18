import os

def get_arg_list(parser):
    args = parser.parse_args()
    return [ arg for arg in args.values() ]

def get_arg_dict(parser):
    args = parser.parse_args()
    return dict(args.items())

def dictkeys_to_lower(d:dict):
    return { k: v for k,v in d.items() }
