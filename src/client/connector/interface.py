import abc
from abc import abstractmethod
from socket import socket


class ConnectorInterface(object, metaclass=abc.ABCMeta):

    @property
    @abstractmethod
    def is_not_alive(self) -> bool:
        """
        Check status connection
        If connection finished -> connection close -> return True
        :return: bool
        """

    @property
    @abstractmethod
    def new_data(self) -> bool:
        """
        Check data in connection
        If exist new data -> return True
        :return: bool (flag new data)
        """

    @abstractmethod
    def execute_bytes(self) -> bytes:
        """
        Execute data until he will br empty
        :return: bytes (data from connection)
        """

    @property
    @abstractmethod
    def socket(self) -> socket:
        """
        Get client socket object
        :return: socket
        """

    @property
    @abstractmethod
    def address(self) -> tuple[str, int]:
        """
        Return client socket address
        :return: tuple[str (host), int (port)]
        """

    @abstractmethod
    async def close_connection(self):
        """
        Make soft close client connection
        :return: None
        """

    @abstractmethod
    async def send(self, data: bytes):
        """
        Send data to connection
        :param data: bytes
        :return: None
        """
