from typing import Optional

import aio_pika
import orjson

from src.publisher.abstract import AbstractPublisher


def check_connection(func):
    async def wrapper(self, *args, **kwargs):
        if not self._conn:
            self.connect()

        return await func(self, *args, **kwargs)
    return wrapper


class RedisPublisher(AbstractPublisher):

    def __init__(self):
        self._conn = None

    def connect(self):
        self._conn = aio_pika.connect("redis://localhost")

    @check_connection
    async def publish_to_destination(
            self,
            data: Optional[list[dict]],
            imei: str
    ):
        if data:
            for d in data:
                await self._conn.lpush(imei, orjson.dumps(d))
