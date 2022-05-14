import json
from typing import Generic, Type, TypedDict, TypeVar

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from .models import Pagination

_FieldT = TypeVar('_FieldT')
_FilterDictT = TypedDict('_FilterDictT', {
    'default': _FieldT | None,
    'example': _FieldT | None,
    'description': str | None
})
_IntDictT = TypedDict('_IntDictT', {
    'default': int | None,
    'example': int | None,
    'description': str | None
})


def get_pagination_parser(offset_kwargs: _IntDictT | None = None,
                          limit_kwargs: _IntDictT | None = None,
                          filter_kwargs: _FilterDictT | None = None):
    _offset_kwargs = {
        'default': 0,
        'ge': 0
    }
    _offset_kwargs.update(offset_kwargs or {})

    _limit_kwargs = {
        'default': 250,
        'ge': 1
    }
    _limit_kwargs.update(limit_kwargs or {})

    _filter_kwargs = {
        'default': None,
        'description': 'Represents values passed to the query as kwargs'
    }
    _filter_kwargs.update(filter_kwargs or {})

    class PageRequestSchema:
        def __init__(self,
                     offset: int = Query(**_offset_kwargs),
                     limit: int | None = Query(**_limit_kwargs),
                     filter: str | None = Query(**_filter_kwargs)):
            self.offset = offset
            self.limit = limit
            self.filter = filter

        def dict(self):
            return {
                'offset': self.offset,
                'limit': self.limit,
                # **(self.filter or {})
            }

    async def _parse_pagination_request(request: Request,
                                        page_request: PageRequestSchema = Depends()) -> Pagination:
        extra_params = {k: v
                        for k, v in request.query_params.items()
                        if k not in ('offset', 'limit')}
        for k, v in extra_params.items():
            try:
                extra_params[k] = json.loads(v)
            except json.JSONDecodeError:
                pass

        return Pagination(
            request=dict(filter(  # filter `None` values
                lambda v: v[1] is not None,
                {
                    **extra_params,
                    **page_request.dict(),
                }.items()
            ))
        )

    return _parse_pagination_request


def generate_response_schema(of_type: Type):
    class PageResponseSchema(BaseModel):
        results: list[of_type]
        count: int
        next: str
        previous: str
    return PageResponseSchema
