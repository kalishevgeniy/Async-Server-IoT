from typing import Optional

import asyncio
import aio_pika
from aio_pika.abc import AbstractRobustConnection, ExchangeType
from aio_pika.pool import Pool
import orjson

from src.publisher.abstract import AbstractPublisher


def check_connection(func):
    async def wrapper(self, *args, **kwargs):
        if not self._is_connected:
            await self.connect()

        return await func(self, *args, **kwargs)
    return wrapper


class RabbitPublisher(AbstractPublisher):

    def __init__(self):
        self._is_connected = False
        self._channel_pool = None
        self._connection_pool = None

    @staticmethod
    async def get_connection() -> AbstractRobustConnection:
        from src.config import Publisher

        return await aio_pika.connect_robust(
            host=Publisher.host,
            login=Publisher.login,
            password=Publisher.password,
            port=Publisher.port,
        )

    async def get_channel(self) -> aio_pika.Channel:
        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    async def publish(self, message) -> None:
        async with self._channel_pool.acquire() as channel:
            await channel.default_exchange.publish(
                message=aio_pika.Message(orjson.dumps(message)),
                routing_key='any'
            )

    async def connect(self):
        self._connection_pool: Pool = Pool(self.get_connection, max_size=2)
        self._channel_pool = Pool(self.get_channel, max_size=10)
        self._is_connected = True

    @check_connection
    async def publish_to_destination(
            self,
            messages: Optional[list[dict]],
            imei: str
    ):
        if not messages:
            return

        async with self._connection_pool, self._channel_pool:
            task_to_publish = [
                asyncio.create_task(self.publish(message))
                for message in messages
            ]
            await asyncio.gather(*task_to_publish)

