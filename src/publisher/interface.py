from abc import abstractmethod, ABCMeta
from typing import Optional


class _InterfacePublisher(metaclass=ABCMeta):

    @abstractmethod
    async def connect(self):
        """
            Make connection for publisher
        """

    @abstractmethod
    async def publish_to_destination(
            self,
            messages: Optional[list[dict]],
            imei: str
    ):
        """
            Publish data to destination
        """


class InterfacePublisher:
    __metaclass__ = _InterfacePublisher
