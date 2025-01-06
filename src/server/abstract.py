from src.client.connections.connection import Command
from src.server.intraface import ServerInterface
from src.utils.datamanager import QueueIter, Data
from src.utils.unit import Unit


class ServerAbstract(ServerInterface):

    async def run(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    async def send_command(self, command: bytes, unit_id) -> Command:
        raise NotImplementedError

    @property
    def messages(self) -> QueueIter[Data]:
        raise NotImplementedError

    @property
    def new_connections(self) -> QueueIter[Unit]:
        raise NotImplementedError
