from uuid import UUID

import aiohttp

from ..exceptions import HTTPNotFoundError

BASE_URL = 'https://api.scryfall.com'


async def does_uuid_exist(uuid: UUID, *, raise_http_error: bool = True) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{BASE_URL}/cards/{uuid}') as res:
            if res.status == 200:
                return True
            if raise_http_error:
                raise HTTPNotFoundError(detail=f"scryfall entry with 'id={uuid}' not found")
            return False
