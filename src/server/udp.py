import asyncio
import logging
from asyncio import DatagramTransport
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.connection import ClientConnection
from src.client.connections_udp import ClientConnectionsUDP
from src.client.connector.UDPconnector import UDPConnector
from src.protocol.abstract import AbstractProtocol
from src.server.intraface import ServerInterface
from src.utils.config import ServerConfig


from src.utils.message import Message


class UDPServerProtocol(asyncio.DatagramProtocol):
    def __init__(
            self,
            protocol,
            msgs_queue: asyncio.Queue,
    ):
        self._transport: Optional[DatagramTransport] = None
        self._msgs_queue = msgs_queue
        self._client_connections = ClientConnectionsUDP()

        self._protocol = protocol

        self._server_is_work: asyncio.Event = asyncio.Event()

    def connection_made(self, transport: DatagramTransport):
        self._transport = transport
        self._server_is_work.set()

    # def connection_lost(self, exc):
    #     print('Connection lost', exc)
    #
    # def pause_writing(self):
    #     print('Pause writing')
    #
    # def resume_writing(self):
    #     print('Resume writing')

    def datagram_received(self, data, addr):
        if addr not in self._client_connections:
            client_connection = ClientConnection(
                msgs_queue=self._msgs_queue,
                protocol=self._protocol,
                server_status=self._server_is_work,
                connector=UDPConnector(
                    address=addr,
                    transport=self._transport
                ),
            )
            self._client_connections.add(client_connection)
        else:
            client_connection = self._client_connections[addr]

        client_connection.connector.udp_data_update(data)

    def error_received(self, exc):
        logging.exception(f'In UDP server get exception: {exc}')

    async def stop(self):
        self._transport.close()
        self._server_is_work.clear()
        await self._client_connections.close_all()


class UDPServer(ServerInterface):
    def __init__(
            self,
            config: ServerConfig,
            protocol: AbstractProtocol,
            authorization: Optional[AbstractAuthorization] = None,
    ):
        self.config = config
        self.protocol = protocol
        self.authorization = authorization

        self._protocol: Optional[UDPServerProtocol] = None
        self._msgs_queue: asyncio.Queue = asyncio.Queue()

    def exec_msgs(self, count: int) -> list[Message]:
        pass

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self._msgs_queue.get()

    async def run(self):
        loop = asyncio.get_running_loop()

        # One protocol instance will be created to serve all
        # client requests.
        _, self._protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(
                protocol=self.protocol,
                msgs_queue=self._msgs_queue,
            ),
            local_addr=('0.0.0.0', 50_000)
        )

    async def stop(self):
        await self._protocol.stop()
