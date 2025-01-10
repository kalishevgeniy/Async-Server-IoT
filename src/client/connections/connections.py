import asyncio
import logging
from functools import wraps

from src.auth.abstract import Authorization
from src.client.connections.connection import ClientConnection


class UnitNotFount(ValueError):
    ...


class ClientConnections:
    def __init__(self):
        # unit.id: ClientConnection
        self._client_connections: [int, ClientConnection] = dict()
        self._unregistered_connections: set[ClientConnection] = set()

    def _monkey_patch_auth(self, func, connection):

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                unit_id = await func(*args, **kwargs)
            except Authorization as e:
                raise

            if unit_id in self._client_connections:
                conn = self._client_connections[unit_id]
                logging.info(f'Close old connection {conn}')
                await conn.close_connection()

            self._unregistered_connections.remove(connection)
            self._client_connections[unit_id] = connection

            return unit_id
        return wrapper

    def add(self, connection: ClientConnection):
        connection.authorization.authorized_in_system = self._monkey_patch_auth(
            func=connection.authorization.authorized_in_system,
            connection=connection
        )
        self._unregistered_connections.add(connection)

    def remove(self, connection: ClientConnection):
        if connection.unit.id in self._client_connections:
            self._client_connections.pop(connection.unit.id, None)
        elif connection in self._unregistered_connections:
            self._unregistered_connections.remove(connection)

    def find(
            self,
            unit_id: int,
    ) -> ClientConnection:
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
