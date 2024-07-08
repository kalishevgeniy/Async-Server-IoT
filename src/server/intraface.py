from abc import ABCMeta, abstractmethod
from typing import Type, Optional

from src.auth.abstract import AbstractAuthorization
from src.protocol.abstract import AbstractProtocol
from src.utils.config import ServerConfig
from src.utils.message import Message


class ServerInterface(object, metaclass=ABCMeta):

    @abstractmethod
    def __init__(
            self,
            config: ServerConfig,
            protocol: AbstractProtocol,
            authorization: Optional[AbstractAuthorization] = None,
    ):
        self.config = config
        self.protocol = protocol
        self.authorization = authorization

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
