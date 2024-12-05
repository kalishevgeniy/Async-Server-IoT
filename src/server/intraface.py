from abc import ABCMeta

from src.auth.abstract import T
from src.client.connections.connection import Command
from src.utils.datamanager import MessagesIter, NewConnectionsIter


class ServerInterface(object, metaclass=ABCMeta):

    async def run(self):
        """
        Run server for input data from gps/iot object
        :return: None
        """
        raise NotImplementedError

    async def stop(self):
        """
        Stop server
        Close server connection, after close clients connections
        :return: None
        """
        raise NotImplementedError

    async def send_command(
            self,
            command: bytes,
            unit_id: T,
    ) -> Command:
        """
        Send command to object connection
        :param unit_id:
        :param command: command to be sent
        :return: ID command use for check answer from object
        """
        raise NotImplementedError

    @property
    def messages(self) -> MessagesIter:
        """
        Return messages iterator
        :return: MessagesIter
        """
        raise NotImplementedError

    @property
    def new_connection(self) -> NewConnectionsIter:
        """
        Return new connections iterator
        :return: NewConnectionsIter
        """
        raise NotImplementedError
