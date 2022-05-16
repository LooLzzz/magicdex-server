import inspect
import json
from typing import Any, Generic, Protocol, TypedDict, TypeVar

from fastapi import HTTPException, Response, status
from pydantic import BaseModel, Field, root_validator

from ..utils import filter_dict_values, url_encoder

_DocType = TypeVar('_DocType', bound=BaseModel)

_paginatable_dict_types = {
    'results': list,
    'total_items': int
}
_paginatable_dict_keys = set(_paginatable_dict_types.keys())
PaginatableDict = TypedDict('PaginatableDict', _paginatable_dict_types)  # type: ignore


class Paginatable(Protocol):
    def __call__(self, *,
                 page_request: 'PageRequest',
                 **kwargs) -> PaginatableDict: ...


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
        params = url_encoder({
            'offset': self.offset,
            'limit': self.limit,
            **self.filter
        })
        return f'{base_url}?{params}'


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

    class Config:
        extra = 'ignore'


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
    base_url: str
    _page: Page[_DocType] | None = None

    async def paginate(self,
                       func: Paginatable,
                       **kwargs) -> 'PageResponse[_DocType]':
        """
        Paginate a function call.
        :param func: The service function to paginate, should accept a `page_request: PageRequest` keyword argument and return a dict with `{'results': [...], 'total_items': ...}`
        :param kwargs: Additional keyword arguments are passed to the service function.
        """
        try:
            if inspect.iscoroutinefunction(func):
                res: PaginatableDict = await func(**kwargs, page_request=self.request)
            else:
                res = func(**kwargs, page_request=self.request)

            if not isinstance(res, dict):
                raise TypeError(
                    f'{func.__name__!r} returned {res.__class__.__name__!r}, '
                    f'expected dict with keys: {_paginatable_dict_keys}'
                )

            res_keys = set(res.keys())
            if not _paginatable_dict_keys.issubset(res_keys):
                raise TypeError(
                    f"{func.__name__!r} returned 'dict' with keys: {res_keys}, "
                    f'expected keys: {_paginatable_dict_keys}'
                )

            self._page = Page.parse_obj({
                **res,
                'request': self.request
            })

        except HTTPException as e:
            raise e

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Error while paginating: {e}',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        return self.response

    @property
    def response(self) -> PageResponse[_DocType]:
        return PageResponse(
            base_url=self.base_url,
            next=self._page.next,
            previous=self._page.previous,
            results=self._page.results,
        )

    class Config:
        underscore_attrs_are_private = True
