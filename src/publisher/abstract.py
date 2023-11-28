from abc import abstractmethod
from typing import Optional

from src.publisher.interface import InterfacePublisher
from src.status.server_status.server import Singleton


class AbstractPublisher(InterfacePublisher, metaclass=Singleton):

    @abstractmethod
    async def connect(self):
        raise NotImplementedError

    @abstractmethod
    async def publish_to_destination(
            self,
            messages: Optional[list[dict]],
            imei: str
    ):
        raise NotImplementedError
