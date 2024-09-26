import asyncio
from src.client.connection import ClientConnection


class ClientConnections:
    def __init__(self):
        self._client_connections: dict[
            tuple[str, int],
            ClientConnection
        ] = dict()

    def __contains__(self, key: tuple[str, int]) -> bool:
        return key in self._client_connections

    def __getitem__(self, item: tuple[str, int]) -> ClientConnection:
        if item in self._client_connections:
            return self._client_connections[item]
        raise AttributeError

    def add(self, connection: ClientConnection):
        self._client_connections[connection.connector.address] = connection

    def remove(self, connection: ClientConnection):
        self._client_connections.pop(connection.connector.address)

    async def close_all(self):
        async with asyncio.TaskGroup() as tg:
            for client in self._client_connections.values():
                tg.create_task(client.close_connection())

        self._client_connections = None
