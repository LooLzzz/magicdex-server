import inspect
from typing import Any, Generic, Protocol, TypeVar
from urllib.parse import urlencode

from bson import ObjectId
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, root_validator

_DocType = TypeVar('_DocType', bound=BaseModel)


class PageRequest(BaseModel):
    offset: int = Field(0, ge=0)
    limit: int | None = Field(None, ge=1)
    filter: dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def build_kwargs(cls, values: dict[str, Any]) -> dict[str, Any]:
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
        params = urlencode({
            'offset': self.offset,
            'limit': self.limit,
            **self.filter
        })
        return f'{base_url}?{params}'


class Page(BaseModel, Generic[_DocType]):
    request: PageRequest
    results: list[_DocType]
    items_left: int

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def total_items(self) -> int:
        return self.request.offset + self.items_left

    @property
    def next(self) -> PageRequest | None:
        next_offset = self.request.offset + (self.request.limit or 0)

        if next_offset <= self.total_items:
            return PageRequest(offset=min(next_offset, self.total_items),
                               limit=self.request.limit,
                               filter=self.request.filter)
        return None

    @property
    def previous(self) -> PageRequest | None:
        prev_offset = self.request.offset - (self.request.limit or 0)

        if prev_offset >= 0:
            return PageRequest(offset=max(0, prev_offset),
                               limit=self.request.limit,
                               filter=self.request.filter)
        return None


class PageResponse(BaseModel, Generic[_DocType]):
    results: list[_DocType] = Field(default_factory=list)
    count: int | None = None
    next: PageRequest | None = None
    previous: PageRequest | None = None
    _base_url: str | None = Field(None, alias='base_url', exclude=True)

    @root_validator()
    def validate_count(cls, values: dict) -> int:
        results: list = values['results']
        count: int = values['count']

        if count is None:
            values['count'] = len(results)
        return values

    def json(self, *args, **kwargs):
        # TODO: why is this not working?
        kwargs['encoder'] = self._encoder
        return super().json(*args, **kwargs)

    def _encoder(self, obj: Any) -> Any:
        if isinstance(obj, PageRequest):
            return obj.generate_url(self._base_url)
        return str(obj)

    class Config:
        allow_population_by_field_name = True
        underscore_attrs_are_private = True


class Paginatable(Protocol, Generic[_DocType]):
    def __acall__(self, *args,
                  page: 'PageRequest',
                  **kwargs) -> Page[_DocType]: ...


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
