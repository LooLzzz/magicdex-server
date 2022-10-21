from abc import ABC
from typing import Any, Generic, Sequence

from pymongo.client_session import ClientSession
from pymongo.collection import Collection, ReturnDocument
from pymongo.cursor import Cursor
from pymongo.results import (DeleteResult, InsertManyResult, InsertOneResult,
                             UpdateResult)
from pymongo.typings import _CollationIn, _DocumentIn, _DocumentType, _Pipeline

_IndexList = Sequence[tuple[str, int | str | dict[str, Any]]]
_IndexKeyHint = str | _IndexList


class AsyncCollection(ABC, Collection, Generic[_DocumentType]):
    """A Mongo async collection."""

    async def insert_one(self,
                         document: _DocumentIn,
                         bypass_document_validation: bool = False,
                         session: ClientSession | None = None,
                         comment: Any | None = None) -> InsertOneResult:
        ...

    async def insert_many(self,
                          documents: list[_DocumentIn],
                          ordered: bool = True,
                          bypass_document_validation: bool = False,
                          session: ClientSession | None = None,
                          comment: Any | None = None) -> InsertManyResult:
        ...

    async def replace_one(self,
                          filter: dict[str, Any],
                          replacement: dict[str, Any],
                          upsert: bool = False,
                          bypass_document_validation: bool = False,
                          collation: _CollationIn | None = None,
                          hint: _IndexKeyHint | None = None,
                          session: ClientSession | None = None,
                          let: dict[str, Any] | None = None,
                          comment: Any | None = None) -> UpdateResult:
        ...

    async def update_one(self,
                         filter: dict[str, Any],
                         update: dict[str, Any] | _Pipeline,
                         upsert: bool = False,
                         bypass_document_validation: bool = False,
                         collation: _CollationIn | None = None,
                         array_filters: Sequence[dict[str, Any]] | None = None,
                         hint: _IndexKeyHint | None = None,
                         session: ClientSession | None = None,
                         let: dict[str, Any] | None = None,
                         comment: Any | None = None) -> UpdateResult:
        ...

    async def update_many(self,
                          filter: dict[str, Any],
                          update: dict[str, Any] | _Pipeline,
                          upsert: bool = False,
                          array_filters: Sequence[dict[str, Any]] | None = None,
                          bypass_document_validation: bool | None = None,
                          collation: _CollationIn | None = None,
                          hint: _IndexKeyHint | None = None,
                          session: ClientSession | None = None,
                          let: dict[str, Any] | None = None,
                          comment: Any | None = None) -> UpdateResult:
        ...

    async def delete_one(self,
                         filter: dict[str, Any],
                         collation: _CollationIn | None = None,
                         hint: _IndexKeyHint | None = None,
                         session: ClientSession | None = None,
                         let: dict[str, Any] | None = None,
                         comment: Any | None = None) -> DeleteResult:
        ...

    async def delete_many(self,
                          filter: dict[str, Any],
                          collation: _CollationIn | None = None,
                          hint: _IndexKeyHint | None = None,
                          session: ClientSession | None = None,
                          let: dict[str, Any] | None = None,
                          comment: Any | None = None) -> DeleteResult:
        ...

    async def find_one(self,
                       filter: Any | None = None,
                       *args: Any,
                       **kwargs: Any) -> dict | None:
        ...

    def find(self,
             *args: Any,
             **kwargs: Any) -> Cursor[dict]:
        ...

    async def count_documents(self,
                              filter: dict[str, Any],
                              session: ClientSession | None = None,
                              comment: Any | None = None,
                              **kwargs: Any) -> int:
        ...

    async def find_one_and_delete(self,
                                  filter: dict[str, Any],
                                  projection: dict[str, Any] | list[str] | None = None,
                                  sort: _IndexList | None = None,
                                  hint: _IndexKeyHint | None = None,
                                  session: ClientSession | None = None,
                                  let: dict[str, Any] | None = None,
                                  comment: Any | None = None,
                                  **kwargs: Any) -> dict:
        ...

    async def find_one_and_replace(self,
                                   filter: dict[str, Any],
                                   replacement: dict[str, Any],
                                   projection: dict[str, Any] | list[str] | None = None,
                                   sort: _IndexList | None = None,
                                   upsert: bool = False,
                                   return_document: bool = ReturnDocument.BEFORE,
                                   hint: _IndexKeyHint | None = None,
                                   session: ClientSession | None = None,
                                   let: dict[str, Any] | None = None,
                                   comment: Any | None = None,
                                   **kwargs: Any,) -> dict:
        ...

    async def find_one_and_update(self,
                                  filter: dict[str, Any],
                                  update: dict[str, Any] | _Pipeline,
                                  projection: dict[str, Any] | list[str] | None = None,
                                  sort: _IndexList | None = None,
                                  upsert: bool = False,
                                  return_document: bool = ReturnDocument.BEFORE,
                                  array_filters: Sequence[dict[str, Any]] | None = None,
                                  hint: _IndexKeyHint | None = None,
                                  session: ClientSession | None = None,
                                  let: dict[str, Any] | None = None,
                                  comment: Any | None = None,
                                  **kwargs: Any) -> dict:
        ...
