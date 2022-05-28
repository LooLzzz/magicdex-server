from abc import ABC
from typing import Any, Generic, Iterable, Mapping, Optional, Sequence

from pymongo.client_session import ClientSession
from pymongo.collection import Collection, ReturnDocument
from pymongo.cursor import Cursor
from pymongo.results import (DeleteResult, InsertManyResult, InsertOneResult,
                             UpdateResult)
from pymongo.typings import _CollationIn, _DocumentIn, _DocumentType, _Pipeline

_IndexList = Sequence[tuple[str, int | str | Mapping[str, Any]]]
_IndexKeyHint = str | _IndexList


class AsyncCollection(ABC, Collection, Generic[_DocumentType]):
    """A Mongo async collection."""

    async def insert_one(self,
                         document: _DocumentIn,
                         bypass_document_validation: bool = False,
                         session: Optional[ClientSession] = None,
                         comment: Optional[Any] = None) -> InsertOneResult:
        ...

    async def insert_many(self,
                          documents: Iterable[_DocumentIn],
                          ordered: bool = True,
                          bypass_document_validation: bool = False,
                          session: Optional[ClientSession] = None,
                          comment: Optional[Any] = None) -> InsertManyResult:
        ...

    async def replace_one(self,
                          filter: Mapping[str, Any],
                          replacement: Mapping[str, Any],
                          upsert: bool = False,
                          bypass_document_validation: bool = False,
                          collation: Optional[_CollationIn] = None,
                          hint: Optional[_IndexKeyHint] = None,
                          session: Optional[ClientSession] = None,
                          let: Optional[Mapping[str, Any]] = None,
                          comment: Optional[Any] = None) -> UpdateResult:
        ...

    async def update_one(self,
                         filter: Mapping[str, Any],
                         update: Mapping[str, Any] | _Pipeline,
                         upsert: bool = False,
                         bypass_document_validation: bool = False,
                         collation: Optional[_CollationIn] = None,
                         array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
                         hint: Optional[_IndexKeyHint] = None,
                         session: Optional[ClientSession] = None,
                         let: Optional[Mapping[str, Any]] = None,
                         comment: Optional[Any] = None) -> UpdateResult:
        ...

    async def update_many(self,
                          filter: Mapping[str, Any],
                          update: Mapping[str, Any] | _Pipeline,
                          upsert: bool = False,
                          array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
                          bypass_document_validation: Optional[bool] = None,
                          collation: Optional[_CollationIn] = None,
                          hint: Optional[_IndexKeyHint] = None,
                          session: Optional[ClientSession] = None,
                          let: Optional[Mapping[str, Any]] = None,
                          comment: Optional[Any] = None) -> UpdateResult:
        ...

    async def delete_one(self,
                         filter: Mapping[str, Any],
                         collation: Optional[_CollationIn] = None,
                         hint: Optional[_IndexKeyHint] = None,
                         session: Optional[ClientSession] = None,
                         let: Optional[Mapping[str, Any]] = None,
                         comment: Optional[Any] = None) -> DeleteResult:
        ...

    async def delete_many(self,
                          filter: Mapping[str, Any],
                          collation: Optional[_CollationIn] = None,
                          hint: Optional[_IndexKeyHint] = None,
                          session: Optional[ClientSession] = None,
                          let: Optional[Mapping[str, Any]] = None,
                          comment: Optional[Any] = None) -> DeleteResult:
        ...

    async def find_one(self,
                       filter: Optional[Any] = None,
                       *args: Any,
                       **kwargs: Any) -> Optional[dict]:
        ...

    def find(self,
             *args: Any,
             **kwargs: Any) -> Cursor[dict]:
        ...

    async def count_documents(self,
                              filter: Mapping[str, Any],
                              session: Optional[ClientSession] = None,
                              comment: Optional[Any] = None,
                              **kwargs: Any) -> int:
        ...

    async def find_one_and_delete(self,
                                  filter: Mapping[str, Any],
                                  projection: Optional[Mapping[str, Any] | Iterable[str]] = None,
                                  sort: Optional[_IndexList] = None,
                                  hint: Optional[_IndexKeyHint] = None,
                                  session: Optional[ClientSession] = None,
                                  let: Optional[Mapping[str, Any]] = None,
                                  comment: Optional[Any] = None,
                                  **kwargs: Any) -> dict:
        ...

    async def find_one_and_replace(self,
                                   filter: Mapping[str, Any],
                                   replacement: Mapping[str, Any],
                                   projection: Optional[Mapping[str, Any] | Iterable[str]] = None,
                                   sort: Optional[_IndexList] = None,
                                   upsert: bool = False,
                                   return_document: bool = ReturnDocument.BEFORE,
                                   hint: Optional[_IndexKeyHint] = None,
                                   session: Optional[ClientSession] = None,
                                   let: Optional[Mapping[str, Any]] = None,
                                   comment: Optional[Any] = None,
                                   **kwargs: Any,) -> dict:
        ...

    async def find_one_and_update(self,
                                  filter: Mapping[str, Any],
                                  update: Mapping[str, Any] | _Pipeline,
                                  projection: Optional[Mapping[str, Any] | Iterable[str]] = None,
                                  sort: Optional[_IndexList] = None,
                                  upsert: bool = False,
                                  return_document: bool = ReturnDocument.BEFORE,
                                  array_filters: Optional[Sequence[Mapping[str, Any]]] = None,
                                  hint: Optional[_IndexKeyHint] = None,
                                  session: Optional[ClientSession] = None,
                                  let: Optional[Mapping[str, Any]] = None,
                                  comment: Optional[Any] = None,
                                  **kwargs: Any) -> dict:
        ...
