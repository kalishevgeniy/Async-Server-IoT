from socket import socket

from src.client.connector.interface import ConnectorInterface


class ConnectorAbstract(ConnectorInterface):

    @property
    def is_not_alive(self) -> bool:
        raise NotImplementedError

    @property
    def new_data(self) -> bool:
        raise NotImplementedError

    def execute_bytes(self) -> bytes:
        raise NotImplementedError

    @property
    def socket(self) -> socket:
        raise NotImplementedError

    @property
    def address(self) -> tuple[str, int]:
        raise NotImplementedError

    async def close_connection(self):
        raise NotImplementedError

    async def send(self, data: bytes):
        raise NotImplementedError
