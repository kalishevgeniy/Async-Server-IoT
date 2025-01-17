import asyncio
import time
from asyncio import StreamReader, StreamWriter, Queue

import logging
from socket import socket

from src.client.connector.abstract import ConnectorAbstract


class ConnectorTCP(ConnectorAbstract):
    __slots__ = (
        "reader", "writer",
        "_reader_queue",
        "_task_reader",
        "timeout",
        "_timeout_timestamp",
        "size",
    )

    def __init__(
            self,
            reader: StreamReader,
            writer: StreamWriter,
            timeout: int = 1200,  # default 10 min
            size: int = 1024    # buffer size
    ):
        self.reader = reader
        self.writer = writer

        self.timeout = timeout
        self._timeout_timestamp = timeout + int(time.time())

        self.size = size

        self._reader_queue: Queue[bytes] = Queue()
        self._task_reader = asyncio.create_task(self._reader_from_socket())

    @property
    def is_not_alive(self) -> bool:
        return (
            self._task_reader.done()
            or
            int(time.time()) > self._timeout_timestamp
        )

    @property
    def new_data(self) -> bool:
        return not self._reader_queue.empty()

    def execute_bytes(self) -> bytes:
        bytes_ = bytes()
        while not self._reader_queue.empty():
            bytes_ += self._reader_queue.get_nowait()
        return bytes_

    def get_socket(self) -> socket:
        return self.writer.get_extra_info('socket')

    async def _reader_from_socket(self):
        try:
            while True:
                data = await self.reader.read(self.size)

                if not data:
                    return True

                await self._reader_queue.put(data)
                self._timeout_timestamp = self.timeout + int(time.time())

        except asyncio.CancelledError:
            raise

    @property
    def address(self) -> tuple[str, int]:
        return self.writer.get_extra_info('peername')

    async def close_connection(self):
        self.writer.close()

        try:
            await asyncio.wait_for(
                self.writer.wait_closed(),
                timeout=10
            )

            if not self._task_reader.done():
                self._task_reader.cancel()

        except asyncio.TimeoutError:
            logging.debug('Close client connection')
        except ConnectionResetError as e:
            _exception = self._task_reader.exception()
            logging.debug(_exception)

    async def send(self, data: bytes):
        if self.is_not_alive:
            raise Exception("Connection was closed")

        if not data:
            return

        self.writer.write(data)
        await self.writer.drain()
