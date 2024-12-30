import asyncio

from src.client.connections.connection import ClientConnection


class UnitNotFount(ValueError):
    ...


class ClientConnections:
    def __init__(self):
        # unit.id: ClientConnection
        self._client_connections: [int, ClientConnection] = dict()
        self._unregistered_connections: set[ClientConnection] = set()

    def add(self, connection: ClientConnection):
        self._unregistered_connections.add(connection)

    def remove(self, connection: ClientConnection):
        if connection.unit.id in self._client_connections:
            self._client_connections.pop(connection.unit.id, None)
        elif connection.unit.id in self._unregistered_connections:
            self._unregistered_connections.remove(connection.unit.id)

    def find(
            self,
            unit_id: int,
    ) -> ClientConnection:
        self._register_new_connection()

        if unit_id in self._client_connections:
            return self._client_connections[unit_id]

        raise UnitNotFount(f'Unit with id {unit_id} not found.')

    async def close_all(self):
        async with asyncio.TaskGroup() as tg:
            for connection in self._client_connections.values():
                tg.create_task(connection.close_connection())

            for connection in self._unregistered_connections:
                tg.create_task(connection.close_connection())

        self._client_connections = dict()
        self._unregistered_connections = set()

    def _register_new_connection(self):
        for un_conn in self._unregistered_connections:
            if un_conn.unit.id:
                self._client_connections[un_conn.unit.id] = un_conn
                self._unregistered_connections.discard(un_conn)
