from abc import ABC, abstractmethod
from typing import Optional

from ..status.server.server import Singleton


class AbstractPublisher(ABC):

    @abstractmethod
    async def connect(self):
        """
            Make connection for publisher
        """

    @abstractmethod
    async def publish_to_destination(
            self,
            data: Optional[list[dict]],
            imei: str
    ):
        """
            Publish data to destination
        """


class AbstractSingleton(metaclass=Singleton):
    pass