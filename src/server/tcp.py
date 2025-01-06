import asyncio
import logging
from asyncio import Server, StreamReader, StreamWriter
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.connections.connection import ClientConnection, Command
from src.client.connections.connections import ClientConnections
from src.client.connector.tcp import ConnectorTCP
from src.protocol.abstract import AbstractProtocol
from src.server.abstract import ServerAbstract
from src.utils.config import ServerConfig
from src.utils.datamanager import DataManager, QueueIter, Data
from src.utils.unit import Unit


class TCPServer(ServerAbstract):
    def __init__(
            self,
            config: ServerConfig,
            protocol: AbstractProtocol,
            authorization: AbstractAuthorization,
    ):
        self.config = config
        self._protocol = protocol
        self._authorization = authorization

        self._server: Optional[Server] = None
        self._server_is_work = asyncio.Event()

        self._client_connections = ClientConnections()
        self._data_manager = DataManager()

    async def run(self):
        logging.info(f"Start server {self._protocol}")

        self._server = await asyncio.start_server(
            self._init_client_connection,
            host=str(self.config.host),
            port=self.config.port,
            **self.config.extra,
        )
        await self._server.start_serving()
        self._server_is_work.set()

    @property
    def messages(self) -> QueueIter[Data]:
        return self._data_manager.messages

    @property
    def new_connections(self) -> QueueIter[Unit]:
        return self._data_manager.new_connections

    async def stop(self):
        logging.info(
            f"Stopping server {self._protocol}. Close server connection"
        )
        await self._soft_stop_server()

        logging.info(
            f"Stopping server {self._protocol}. Close clients connection"
        )
        # stop current work task clients
        self._server_is_work.clear()

        # cancel current task work and close connection
        await self._client_connections.close_all()
        logging.info(
            f"All client connections closed, server {self._protocol} stopped."
        )

    async def send_command(
            self,
            command: bytes,
            unit_id,
    ) -> Command:

        conn = self._client_connections.find(
            unit_id=unit_id,
        )
        command_send = await conn.send_command(command)
        return command_send

    async def _init_client_connection(
            self,
            reader: StreamReader,
            writer: StreamWriter,
            **kwargs
    ):
        client_conn = ClientConnection(
            data_manager=self._data_manager,
            protocol=self._protocol,
            authorization=self._authorization,
            connector=ConnectorTCP(reader=reader, writer=writer),
            server_status=self._server_is_work,
            config=self.config,
            **kwargs
        )

        self._client_connections.add(client_conn)
        try:
            await client_conn.run_client_loop()
        except NotImplementedError as e:
            logging.exception(f"Warning! Method not implemented {e}")
        except Exception as e:
            logging.exception(f"Unknown exception! {e}")
        finally:
            # make soft disconnect
            await client_conn.close_connection()

            # remove curr task from event loop
            # use for keeping connection
            logging.debug(f"Client disconnect {client_conn}")
            self._client_connections.remove(client_conn)

    async def _soft_stop_server(self):
        self._server.close()
        try:
            await asyncio.wait_for(
                self._server.wait_closed(),
                15
            )
        except asyncio.TimeoutError:
            logging.warning('Timeout error close socket')
