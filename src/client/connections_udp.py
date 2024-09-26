import asyncio
from src.client.connection import ClientConnection
from src.client.connections import ClientConnections


class ClientConnectionsUDP(ClientConnections):
    def __init__(self):
        super().__init__()
        self.running_tasks: dict[ClientConnection, asyncio.Task] = dict()

    def add(self, connection: ClientConnection):
        task = asyncio.create_task(connection.run_client_loop())
        self.running_tasks[connection] = task

        super().add(connection)

    def remove(self, connection: ClientConnection):
        task = self.running_tasks.pop(connection)
        task.cancel()

        super().remove(connection)
