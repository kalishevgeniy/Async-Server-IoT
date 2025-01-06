import asyncio
import logging
import time
from asyncio import DatagramTransport
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.connections.connection import ClientConnection, Command, Data
from src.client.connections.connections import ClientConnections
from src.client.connector.udp import ConnectorUDP
from src.protocol.abstract import AbstractProtocol
from src.server.abstract import ServerAbstract
from src.utils.config import ServerConfig
from src.utils.datamanager import DataManager, QueueIter
from src.utils.unit import Unit


class UDPServerProtocol(asyncio.DatagramProtocol, ServerAbstract):

    def __init__(
            self,
            protocol,
            authorization: AbstractAuthorization,
            config: ServerConfig
    ):
        self._transport: Optional[DatagramTransport] = None
        self._data_manager = DataManager()
        self._authorization = authorization
        self._client_connections = ClientConnections()
        self._config = config

        self._protocol = protocol
        self._server_is_work: asyncio.Event = asyncio.Event()

        self._connection_objects: dict = dict()

    def connection_made(self, transport: DatagramTransport):  # type: ignore
        self._transport = transport
        self._server_is_work.set()

    def connection_lost(self, exc):
        logging.exception(f'UDP connection lost: {exc} {self}')

    def pause_writing(self):
        logging.exception(f'UDP pause writing {self}')

    def resume_writing(self):
        logging.exception(f'UDP resume writing {self}')

    async def _run_client_connection(
            self,
            client_connection: ClientConnection
    ):
        try:
            _runtime = time.time()

            client_loop_task = asyncio.create_task(
                client_connection.run_client_loop()
            )
            while (
                    client_loop_task.done()
                    or
                    _runtime + self._config.timeout > time.time()
            ):
                await asyncio.sleep(1)

            if client_loop_task.exception():
                raise client_loop_task.exception()

        except NotImplementedError as e:
            logging.exception(f"Warning! Method not implemented {e}")
        except Exception as e:
            logging.exception(f"Unknown exception! {e}")
        finally:
            await client_connection.close_connection()

            logging.debug(f"Client disconnect {client_connection}")
            self._client_connections.remove(client_connection)

    def datagram_received(self, data, addr):
        if addr not in self._connection_objects:
            client_connection = ClientConnection(
                data_manager=self._data_manager,
                server_status=self._server_is_work,
                authorization=self._authorization,
                protocol=self._protocol,
                config=self._config,
                connector=ConnectorUDP(
                    address=addr,
                    transport=self._transport
                ),
            )
            asyncio.create_task(client_connection.run_client_loop())

            self._client_connections.add(connection=client_connection)
            self._connection_objects[addr] = client_connection

        else:
            client_connection = self._connection_objects[addr]

        client_connection.buffer.update(data)

    def error_received(self, exc):
        logging.exception(f'In UDP server get exception: {exc}')

    async def stop(self):
        self._transport.close()
        self._server_is_work.clear()
        await self._client_connections.close_all()

    async def run(self):
        await asyncio.sleep(0)

    async def send_command(self, command: bytes, unit_id) -> Command:
        client_connection = self._client_connections.find(unit_id)
        command_send = await client_connection.send_command(command)
        return command_send

    @property
    def messages(self) -> QueueIter[Data]:
        return self._data_manager.messages

    @property
    def new_connections(self) -> QueueIter[Unit]:
        return self._data_manager.new_connections


class UDPServer(ServerAbstract):
    def __init__(
            self,
            config: ServerConfig,
            protocol: AbstractProtocol,
            authorization: AbstractAuthorization,
    ):
        self._server = UDPServerProtocol(
                protocol=protocol,
                authorization=authorization,
                config=config
        )
        self.config = config
        self._messages = DataManager()

    async def run(self):
        loop = asyncio.get_running_loop()

        # One protocol instance will be created to serve all
        # client requests.
        _, self._server = await loop.create_datagram_endpoint(
            lambda: self._server,
            local_addr=(str(self.config.host), self.config.port)
        )

    async def stop(self):
        await self._server.stop()

    async def send_command(self, command: bytes, unit_id) -> Command:
        return await self._server.send_command(command, unit_id)

    @property
    def messages(self) -> QueueIter[Data]:
        return self._server.messages

    @property
    def new_connections(self) -> QueueIter[Unit]:
        return self._server.new_connections

