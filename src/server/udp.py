import asyncio
import logging
import time
from asyncio import DatagramTransport, transports
from typing import Optional

from src.auth.abstract import AbstractAuthorization, T
from src.client.connections.connection import ClientConnection, Command
from src.client.connections.connections import ClientConnections
from src.client.connector.udp import ConnectorUDP
from src.protocol.abstract import AbstractProtocol
from src.server.abstract import ServerAbstract
from src.utils.config import ServerConfig
from src.utils.datamanager import DataManager, MessagesIter, NewConnectionsIter


class UDPServerProtocol(asyncio.DatagramProtocol, ServerAbstract):

    def __init__(
            self,
            protocol,
            authorization: AbstractAuthorization,
    ):
        self._transport: Optional[DatagramTransport] = None
        self._data_manager = DataManager()
        self._authorization = authorization
        self._client_connections = ClientConnections()

        self._protocol = protocol
        self._server_is_work: asyncio.Event = asyncio.Event()

        self.__connections_addresses = dict()

    def connection_made(self, transport: DatagramTransport):  # type: ignore
        self._transport = transport
        self._server_is_work.set()

    def connection_lost(self, exc):
        logging.exception(f'UDP connection lost: {exc} {self}')

    def pause_writing(self):
        logging.exception(f'UDP pause writing {self}')

    def resume_writing(self):
        logging.exception(f'UDP resume writing {self}')

    def datagram_received(self, data, addr):
        if addr not in self.__connections_addresses:
            client_connection = ClientConnection(
                data_manager=self._data_manager,
                server_status=self._server_is_work,
                authorization=self._authorization,
                protocol=self._protocol,
                connector=ConnectorUDP(
                    address=addr,
                    transport=self._transport
                ),
            )
            task = asyncio.create_task(client_connection.run_client_loop())
            self._client_connections.add(client_connection)
            self.__connections_addresses[addr] = (
                client_connection,
                task,
                time.time()
            )
        else:
            client_connection = self.__connections_addresses[addr][0]

        client_connection.buffer.update(data)

    def error_received(self, exc):
        logging.exception(f'In UDP server get exception: {exc}')

    async def stop(self):
        self._transport.close()
        self._server_is_work.clear()
        await self._client_connections.close_all()

    async def run(self):
        await asyncio.sleep(0)

    async def send_command(self, command: bytes, unit_id: T) -> Command:
        client_connection = self._client_connections.find(unit_id)
        command_send = await client_connection.send_command(command)
        return command_send

    @property
    def messages(self) -> MessagesIter:
        return self._data_manager.messages

    @property
    def new_connection(self) -> NewConnectionsIter:
        return self._data_manager.new_connections


class UDPServer(ServerAbstract):
    def __init__(
            self,
            config: ServerConfig,
            protocol: AbstractProtocol,
            authorization: AbstractAuthorization,
    ):
        self._config = config
        self._protocol_parsing = protocol
        self._authorization = authorization

        self._protocol: Optional[UDPServerProtocol] = None
        self._messages = DataManager()

    async def run(self):
        loop = asyncio.get_running_loop()

        # One protocol instance will be created to serve all
        # client requests.
        _, self._protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(
                protocol=self._protocol,
                authorization=self._authorization,
            ),
            local_addr=(str(self._config.host), self._config.port)
        )

    async def stop(self):
        await self._protocol.stop()

    async def send_command(self, command: bytes, unit_id: T) -> Command:
        return await self._protocol.send_command(command, unit_id)

    @property
    def messages(self) -> MessagesIter:
        return self._protocol.messages

    @property
    def new_connection(self) -> NewConnectionsIter:
        return self._protocol.new_connection
