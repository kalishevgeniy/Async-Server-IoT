import asyncio
from dataclasses import dataclass
from collections.abc import AsyncIterator, AsyncGenerator
from datetime import datetime
from time import time
from typing import Generic, TypeVar

from src.protocol.interface import MessageAnnotated
from src.utils.unit import Unit

T = TypeVar("T")


@dataclass
class Packet:
    packet: bytes
    client_port: int
    client_ip: str
    time_received: datetime

    def __repr__(self):
        return (
            f"<Packet "
            f"ip={self.client_ip}, "
            f"port={self.client_port}, "
            f"time={self.time_received}, "
            f"packet={self.packet[:20].decode()}..."
            f">"
        )


@dataclass
class Command:
    command_body: bytes
    command_send: bytes
    time_sent: float = time()


@dataclass
class Data:
    unit: Unit
    packet: Packet
    answer: bytes
    messages: list[MessageAnnotated]


class QueueIter(Generic[T], AsyncIterator):
    def __init__(
            self,
            max_size=500,
            clear_on_overflow=False,
    ):
        self._queue = asyncio.Queue(maxsize=max_size)
        self._clear_on_overflow = clear_on_overflow

    async def __anext__(self):
        while not self._queue.empty():
            return await self._queue.get()

        await asyncio.sleep(0)
        raise StopAsyncIteration

    def __aiter__(self):
        return self

    async def inf(self) -> AsyncGenerator[T]:
        while True:
            yield await self._queue.get()

    async def put(self, item: T):
        if self._clear_on_overflow:
            try:
                self._queue.put_nowait(item)
            except asyncio.QueueFull:
                self._queue.get_nowait()
                self._queue.put_nowait(item)

            await asyncio.sleep(0)
        else:
            await self._queue.put(item)

    async def get(self) -> T:
        return await self._queue.get()


class DataManager:
    def __init__(self):
        self._messages_iter: QueueIter[Data] = QueueIter()
        self._new_connections_iter: QueueIter[Unit] = QueueIter(
            clear_on_overflow=True
        )
        self._disconnect_iter: QueueIter[Unit] = QueueIter(
            clear_on_overflow=True
        )

    @property
    def messages(self) -> QueueIter[Data]:
        return self._messages_iter

    @property
    def new_connections(self) -> QueueIter[Unit]:
        return self._new_connections_iter

    @property
    def disconnects(self) -> QueueIter[Unit]:
        return self._disconnect_iter
