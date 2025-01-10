import asyncio
import time
from asyncio import DatagramTransport

import logging
from socket import socket

from src.client.connector.abstract import ConnectorAbstract


class ConnectorUDP(ConnectorAbstract):
    def __init__(
            self,
            address: tuple,
            transport: DatagramTransport,
            timeout: int = 1200  # default 10 min
    ):
        self._ip, self._port = address

        self._data = bytes()
        self._is_not_alive = False

        self.__transport = transport

        self.timeout = timeout
        self._timeout_timestamp = timeout + int(time.time())

    @property
    def is_not_alive(self) -> bool:
        return (
                self._is_not_alive
                or
                int(time.time()) > self._timeout_timestamp
        )

    @property
    def new_data(self) -> bool:
        return True if self._data else False

    def execute_bytes(self) -> bytes:
        data = self._data[:]
        self._data = bytes()
        return data

    @property
    def socket(self) -> socket:
        logging.warning('Socket client UDP it is soket server!')
        return self.__transport.get_extra_info('socket')

    @property
    def address(self) -> tuple[str, int]:
        return self._ip, self._port

    async def close_connection(self):
        self._is_not_alive = True
        await asyncio.sleep(0)

    async def send(self, data: bytes):
        self.__transport.sendto(data, (self._ip, self._port))
        await asyncio.sleep(0)

    def update(self, data: bytes):
        self._data += data
        self._timeout_timestamp = self.timeout + int(time.time())
