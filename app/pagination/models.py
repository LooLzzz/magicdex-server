import inspect
import json
from typing import Any, Generic, Protocol, TypeVar
from urllib.parse import urlencode

from fastapi import HTTPException, Response, status
from pydantic import BaseModel, Field, root_validator

from ..utils import filter_dict_values

_DocType = TypeVar('_DocType', bound=BaseModel)


class Paginatable(Protocol, Generic[_DocType]):
    def __call__(self, *args,
                 page_request: 'PageRequest',
                 **kwargs) -> 'Page[_DocType]': ...


class PageRequest(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int | None = Field(None, ge=1)
    filter: dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def build_filter_dict(cls, values: dict[str, Any]) -> dict[str, Any]:
        all_required_field_names = {field.alias
                                    for field in cls.__fields__.values()
                                    if field.alias != 'filter'}  # to support alias

        filter: dict[str, Any] = values.pop('filter', None) or {}
        for field_name in list(values):
            if field_name not in all_required_field_names:
                filter[field_name] = values.pop(field_name)

        values['filter'] = filter
        return values

    def generate_url(self, base_url: str) -> str:
        params = urlencode(
            filter_dict_values({
                'offset': self.offset,
                'limit': self.limit,
                **self.filter
            })
        )
        return f'{base_url}?{params}'

    def dict(self, *args, **kwargs):
        return self  # required for hacky fix


class Page(BaseModel, Generic[_DocType]):
    request: PageRequest
    results: list[_DocType]
    total_items: int

    @property
    def has_next(self) -> bool:
        return self.request.limit is not None and self.request.offset + self.request.limit < self.total_items

    @property
    def has_previous(self) -> bool:
        return self.request.offset > 0

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def items_left(self) -> int:
        return self.total_items - self.count - self.request.offset

    @property
    def next(self) -> PageRequest | None:
        if self.has_next:
            return PageRequest(offset=self.request.offset + (self.request.limit or 0),
                               limit=self.request.limit,
                               filter=self.request.filter)
        return None

    @property
    def previous(self) -> PageRequest | None:
        if self.has_previous:
            return PageRequest(offset=max(0, self.request.offset - (self.request.limit or self.count)),
                               limit=self.request.limit,
                               filter=self.request.filter)
        return None


class PageResponse(Response, Generic[_DocType]):
    def __init__(self, results: list[_DocType] | None = None,
                 count: int | None = None,
                 next: PageRequest | None = None,
                 previous: PageRequest | None = None,
                 base_url: str | None = None):
        self._base_url = base_url
        self._content = {'count': count or len(results),
                         'next': next,
                         'previous': previous,
                         'results': results},

        super().__init__(content=self.json(),
                         media_type='application/json')

    def json(self, *, sort_keys: bool = False, **kwargs) -> str:
        def encoder(obj):
            if isinstance(obj, PageRequest):
                return obj.generate_url(self._base_url)
            if isinstance(obj, BaseModel):
                return obj.dict()
            return str(obj)

        return json.dumps(
            self._content,
            **kwargs,
            sort_keys=sort_keys,
            default=encoder
        )


class Pagination(BaseModel, Generic[_DocType]):
    request: PageRequest
    _endpoint_url: str | None = None
    _page: Page[_DocType] | None = None

    async def paginate(self, endpoint_url: str,
                       func: Paginatable[_DocType],
                       *args, **kwargs) -> 'Pagination[_DocType]':
        """
        Paginate a function call.
        Any additional arguments are passed to the function.
        :param endpoint_url: The endpoint URL to use for the pagination links
        :param func: The function to paginate, should accept a `page_request: PageRequest` kwarg and return a `pagination.Page` or its values as a `dict`
        """
        self._endpoint_url = endpoint_url

        try:
            if inspect.iscoroutinefunction(func):
                self._page = Page.parse_obj(
                    await func(*args, **kwargs, page_request=self.request)
                )
            else:
                self._page = Page.parse_obj(
                    func(*args, **kwargs, page_request=self.request)
                )

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Error while paginating: {e!r}',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        return self

    @property
    def response(self) -> PageResponse[_DocType]:
        return PageResponse(
            base_url=self._endpoint_url,
            next=self._page.next,
            previous=self._page.previous,
            results=self._page.results,
        )

    class Config:
        underscore_attrs_are_private = True
