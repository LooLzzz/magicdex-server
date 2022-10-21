"""
### Imports
```py
import pagination as pg
```

---

### Routes
```py
@router.get(..., response_model=pg.generate_response_schema(SomeModel))
async def some_route(
    pagination: pg.Pagination[SomeModel] = Depends(
        pg.get_pagination_dependency(offset_kwargs={...},
                                     limit_kwargs={...},
                                     filter_kwargs={...})
    ),
    ...  # additional route dependencies goes here
):
    return await pagination.paginate(
        func=db_query_func,
        ...  # func kwargs goes here
    )
```

---

### Services
```py
async def db_query_func(page_request: PageRequest, **extra_kwargs) -> pg.PaginatableDict:
    ...  # db query logic goes here

    return {
        'results': results,
        'total_items': total_items
    }
```
"""

from .models import *
from .services import *
