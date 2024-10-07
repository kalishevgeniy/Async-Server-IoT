from abc import ABCMeta
from typing import Optional

from src.utils.message import Message


class ServerInterface(object, metaclass=ABCMeta):

    def exec_msgs(self, count: int) -> list[Message]:
        """
        Return message already get
        :return:
        """
        raise NotImplementedError

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
            unit_id: Optional[int] = None,
            imei: Optional[str] = None,
    ) -> int:
        """
        Send command to object connection
        :param unit_id: used ONLY with class AbstractAuthorization!
        :param imei: unique identifier of object
        :param command: command to be sent
        :return: ID command use for check answer from object
        """
        raise NotImplementedError
