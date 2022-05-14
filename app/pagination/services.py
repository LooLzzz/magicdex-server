from cProfile import label
from typing import Any, TypedDict, TypeVar

from fastapi import Depends, Query, Request
from traitlets import default

from .models import Pagination

_FilterT = TypeVar('_FilterT')
_FilterDictT = TypedDict('_FilterDictT', {
    'default': _FilterT,
    'example': _FilterT,
    'description': str | None
})


def get_pagination_parser(offset_default: int = 0,
                          limit_default: int | None = 250,
                          filter_kwargs: _FilterDictT | None = None):
    _filter_kwargs = {
        'default': None,
        'description': 'Represents values passed to the query as kwargs'
    }
    _filter_kwargs.update(filter_kwargs or {})

    class PageRequestSchema:
        def __init__(self,
                     offset: int = Query(offset_default, ge=0),
                     limit: int | None = Query(limit_default, ge=1),
                     filter: str | None = Query(**_filter_kwargs)):
            self.offset = offset
            self.limit = limit
            self.filter = filter

        def dict(self):
            return {
                'offset': self.offset,
                'limit': self.limit,
                **(self.filter or {})
            }

    async def _parse_pagination_request(request: Request,
                                        page_request: PageRequestSchema = Depends()) -> Pagination:
        return Pagination(
            request=dict(filter(  # filter `None` values
                lambda v: v[1] is not None,
                {
                    **page_request.dict(),
                    **{k: v
                       for k, v in request.query_params.items()
                       if k not in ('offset', 'limit')}
                }.items()
            ))
        )

    return _parse_pagination_request
