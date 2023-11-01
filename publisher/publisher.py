from typing import Optional

from redis import asyncio as aioredis
import orjson

from ..publisher.abstract_publisher import AbstractSingleton


def check_connection(func):
    async def wrapper(self, *args, **kwargs):
        if not self._conn:
            self.connect()

        return await func(self, *args, **kwargs)
    return wrapper


class RedisPublisher(AbstractSingleton):

    def __init__(self):
        self._conn = None

    def connect(self):
        self._conn = aioredis.from_url("redis://localhost")

    @check_connection
    async def publish_to_destination(
            self,
            data: Optional[list[dict]],
            imei: str
    ):
        if data:
            for d in data:
                await self._conn.lpush(imei, orjson.dumps(d))
