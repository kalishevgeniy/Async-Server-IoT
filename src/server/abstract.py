from abc import ABCMeta

from src.auth.abstract import T
from src.client.connections.connection import Command
from src.server.intraface import ServerInterface
from src.utils.datamanager import MessagesIter, NewConnectionsIter


class ServerAbstract(ServerInterface):

    async def run(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError

    async def send_command(self, command: bytes, unit_id: T) -> Command:
        raise NotImplementedError

    @property
    def messages(self) -> MessagesIter:
        raise NotImplementedError

    @property
    def new_connection(self) -> NewConnectionsIter:
        raise NotImplementedError
