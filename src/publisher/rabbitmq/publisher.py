from typing import Optional

import asyncio
import aio_pika
from aio_pika.abc import AbstractRobustConnection, ExchangeType
from aio_pika.pool import Pool
import orjson

from src.config import Publisher
from src.publisher.abstract import AbstractPublisher
from src.utils.logger import Logger


def check_connection(func):
    async def wrapper(self, *args, **kwargs):
        if not self._is_connected:
            await self.connect()

        return await func(self, *args, **kwargs)
    return wrapper


class RabbitPublisher(AbstractPublisher):

    def __init__(self):
        self._is_connected = False
        self._connected_event = asyncio.Event()

        self._channel_pool = None
        self._connection_pool = None

    @staticmethod
    async def get_connection() -> AbstractRobustConnection:
        return await aio_pika.connect_robust(
            host=Publisher.host,
            login=Publisher.login,
            password=Publisher.password,
            port=Publisher.port,
        )

    async def get_channel(self) -> aio_pika.Channel:
        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    async def __declare_exchange(
            self,
            name: str = Publisher.exchange,
            type_exchange: ExchangeType = Publisher.exchange_type,
            *kwargs,
            **args,
    ):
        async with self._channel_pool.acquire() as channel:
            return await channel.declare_exchange(
                name=name,
                type=type_exchange,
                *kwargs,
                **args
            )

    async def __declare_queue(
            self,
            name: str = Publisher.queue_name,
            *args,
            **kwargs
    ):
        async with self._channel_pool.acquire() as channel:
            return await channel.declare_queue(
                name=name,
                *args,
                **kwargs
            )

    async def _declare_rabbit_entity(self):
        self._exchange = await self.__declare_exchange()
        self._queue = await self.__declare_queue()

        await self._queue.bind(
            exchange=self._exchange,
            routing_key=Publisher.routing_key
        )

    async def connect(self):
        if not self._connected_event.is_set():
            Logger().info('Make connection rabbit')
            self._connection_pool = Pool(self.get_connection, max_size=2)
            self._channel_pool = Pool(self.get_channel, max_size=10)

            await self._declare_rabbit_entity()

            self._is_connected = True
            self._connected_event.clear()
        else:
            Logger().debug('Connection for rabbit try made')
            await asyncio.sleep(1)

    async def publish(self, message) -> None:
        async with self._channel_pool.acquire() as channel:
            # Reopen channels that have been closed previously
            if channel.is_closed:
                await channel.reopen()

            Logger().info(f"Publish message to rabbit - {message}")
            await channel.basic_publish(
                exchange=Publisher.exchange,
                body=orjson.dumps(message),
                routing_key=Publisher.routing_key,
            )

    @check_connection
    async def publish_to_destination(
            self,
            messages: Optional[list[dict]],
            imei: str
    ):
        if not messages:
            return

        task_to_publish = [
            asyncio.create_task(self.publish(message))
            for message in messages
        ]
        await asyncio.gather(*task_to_publish)
