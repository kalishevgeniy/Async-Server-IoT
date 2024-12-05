import asyncio
from src.client.connections.connection import ClientConnection


class UnitNotFount(ValueError):
    ...


class ClientConnections:
    def __init__(self):
        self._client_connections = dict()
        self._ind = dict()
        self._new_connections: set[ClientConnection] = set()

    def add(self, connection: ClientConnection):
        self._new_connections.add(connection)
        self._register_new_connection()

    def remove(self, connection: ClientConnection):

        ind_ = self._ind.pop(connection.__hash__(), None)

        if ind_:
            self._client_connections.pop(ind_, None)
        else:
            self._new_connections.remove(connection)

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

            for connection in self._new_connections:
                tg.create_task(connection.close_connection())

        self._client_connections = None
        self._new_connections = None
        self._ind = None

    def _register_new_connection(self):
        for new_connection in self._new_connections:
            if id_ := new_connection.authorization.id:
                self._client_connections[id_] = new_connection
                self._ind[new_connection.__hash__()] = id_

                self._new_connections.discard(id_)
