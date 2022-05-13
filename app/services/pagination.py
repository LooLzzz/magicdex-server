from fastapi import Depends, Request

from .. import models


async def parse_pagination(request: Request,
                           offset: int | None = None,
                           limit: int | None = None) -> models.Pagination:
    extra_params = {k: v
                    for k, v in request.query_params.items()
                    if k not in ('offset', 'limit')}

    return models.Pagination(
        request=dict(filter(
            lambda v: v[1] is not None,
            {'offset': offset,
             'limit': limit,
             **extra_params}.items()
        ))
    )
