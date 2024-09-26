from abc import ABCMeta
from src.utils.message import Message


class ServerInterface(object, metaclass=ABCMeta):

    def exec_msgs(self, count: int) -> list[Message]:
        """
        Return message already get
        :return:
        """
        raise NotImplementedError

    async def run(self):
        raise NotImplementedError

    async def stop(self):
        raise NotImplementedError
