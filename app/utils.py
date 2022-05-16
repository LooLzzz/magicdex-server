from typing import Callable, TypeVar
from urllib.parse import urlencode

_KeyType = TypeVar('_KeyType')
_ValueType = TypeVar('_ValueType')


def filter_dict_values(d: dict[_KeyType, _ValueType],
                       filter_func: Callable[[_ValueType], bool] | None = None) -> dict[_KeyType, _ValueType]:
    """
    Filter dict values by `filter_func`
    :param d: dict to filter
    :param filter_func: filter function, defaults to `(lambda v: v is not None)`
    """
    filter_func = filter_func or (lambda v: v is not None)
    return {k: v
            for k, v in d.items()
            if filter_func(v)}


def url_encoder(value) -> str:
    if isinstance(value, dict):
        return urlencode([
            (k, url_encoder(v)) for k, v
            in filter_dict_values(value).items()
        ])

    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, list | tuple):
        return repr(value).replace("'", '"')
    return value
