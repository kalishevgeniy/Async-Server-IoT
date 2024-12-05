import asyncio
from collections.abc import AsyncIterator


class NewConnectionsIter(AsyncIterator):

    def __init__(self):
        self._new_connections_iter = asyncio.Queue()

    async def __anext__(self):
        while not self._new_connections_iter.empty():
            return await self._new_connections_iter.get()
        raise StopAsyncIteration

    def __aiter__(self):
        return self

    async def put(self, item):
        await self._new_connections_iter.put(item)

    async def get(self):
        return await self._new_connections_iter.get()


class MessagesIter(AsyncIterator):

    def __init__(self):
        self._messages = asyncio.Queue()

    async def __anext__(self):
        while not self._messages.empty():
            return await self._messages.get()
        raise StopAsyncIteration

    def __aiter__(self):
        return self

    async def put(self, item):
        await self._messages.put(item)

    async def get(self):
        return await self._messages.get()


class DataManager:
    def __init__(self):
        self._messages_iter = MessagesIter()
        self._new_connections_iter = NewConnectionsIter()

    @property
    def messages(self):
        return self._messages_iter

    @property
    def new_connections(self):
        return self._new_connections_iter
