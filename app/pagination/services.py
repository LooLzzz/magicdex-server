import json
from typing import Type, TypedDict, TypeVar

from fastapi import Depends, Query, Request
from pydantic import BaseModel

from ..utils import filter_dict_values
from .models import Pagination

_FieldT = TypeVar('_FieldT')
_FilterFieldDictT = TypedDict('_FilterFieldDictT', {
    'default': _FieldT | None,
    'example': _FieldT | None,
    'description': str | None
})
_IntFieldDictT = TypedDict('_IntFieldDictT', {
    'default': int | None,
    'example': int | None,
    'description': str | None
})


def get_pagination_dependency(offset_kwargs: _IntFieldDictT | None = None,
                              limit_kwargs: _IntFieldDictT | None = None,
                              filter_kwargs: _FilterFieldDictT | None = None):
    offset_kwargs = {
        'default': 0,
        'ge': 0,
        **(offset_kwargs or {})
    }

    limit_kwargs = {
        'default': 250,
        'ge': 1,
        **(limit_kwargs or {})
    }

    filter_kwargs = {
        'default': None,
        'description': 'Represents values passed to the query as kwargs',
        **(filter_kwargs or {})
    }

    class PageRequestSchema:
        def __init__(self,
                     offset: int = Query(**offset_kwargs),
                     limit: int | None = Query(**limit_kwargs),
                     filter: str | None = Query(**filter_kwargs)):
            self.offset = offset
            self.limit = limit
            # ignore filter, it will be handled by 'pg.Pagination'

        def dict(self):
            return {
                'offset': self.offset,
                'limit': self.limit,
            }

    async def _parse_pagination_request(request: Request,
                                        page_request: PageRequestSchema = Depends()) -> Pagination:
        base_url = str(request.url).split('?')[0]
        extra_params = {k: v
                        for k, v in request.query_params.items()
                        if k not in ('offset', 'limit')}
        for k, v in extra_params.items():
            try:
                extra_params[k] = json.loads(v)
            except json.JSONDecodeError:
                pass  # do nothing

        return Pagination(
            # filter `None` values
            base_url=base_url,
            request=filter_dict_values({
                **extra_params,
                **page_request.dict(),
            })
        )

    return _parse_pagination_request


def generate_response_schema(of_type: Type):
    class PageResponseSchema(BaseModel):
        results: list[of_type]
        count: int
        next: str
        previous: str
    return PageResponseSchema
