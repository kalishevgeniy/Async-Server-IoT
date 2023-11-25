from typing import Optional

import aio_pika
import orjson

from src.publisher.abstract import AbstractPublisher


class RabbitPublisher(AbstractPublisher):

    def __init__(self):
        self._conn = None

    async def connect(self):
        self._conn = await aio_pika.connect("amqp://test:test@localhost/")
        # # Creating a channel
        # channel = await self._conn.channel()
        #
        # # Declaring queue
        # queue = await channel.declare_queue("hello")

    async def publish_to_destination(
            self,
            data: Optional[list[dict]],
            imei: str
    ):
        if data:
            for d in data:
                await self._conn(imei, orjson.dumps(d))
