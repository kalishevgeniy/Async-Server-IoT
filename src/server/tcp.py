import asyncio
from asyncio import Server, StreamReader, StreamWriter
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.connection import ClientConnection
from src.client.connections import ClientConnections
from src.client.connector.TCPReaderWriter import TCPReaderWriter
from src.protocol.abstract import AbstractProtocol
from src.server.intraface import ServerInterface
from src.unit.unit import Unit
from src.utils.config import ServerConfig

import logging

from src.utils.message import Message


class TCPServer(ServerInterface):
    def __init__(
            self,
            config: ServerConfig,
            protocol: AbstractProtocol,
            authorization: Optional[AbstractAuthorization] = None,
    ):
        self.config = config
        self.protocol = protocol
        self.authorization = authorization

        self._server: Optional[Server] = None
        self._server_is_work: asyncio.Event = asyncio.Event()

        self._client_connections: ClientConnections = ClientConnections()
        # self._commands: Commands = Commands()

        self._msgs_queue = asyncio.Queue(config.queue_size)

    def __aiter__(self):
        return self

    async def __anext__(self):
        message = await self._msgs_queue.get()
        return message

    def exec_msgs(self, count: int = -1) -> list[Message]:
        msgs = list()
        while not self._msgs_queue.empty() and len(msgs) > count:
            msgs.append(self._msgs_queue.get_nowait())
        return msgs

    async def run(self):
        self._server = await asyncio.start_server(
            self._init_client_connection,
            host=str(self.config.host),
            port=self.config.port,
            **self.config.model_extra,
        )
        await self._server.start_serving()

        self._server_is_work.set()

    async def _soft_stop_server(self):
        self._server.close()
        try:
            await asyncio.wait_for(
                self._server.wait_closed(),
                15
            )
        except asyncio.TimeoutError:
            logging.warning('Timeout error close socket')

    async def stop(self):
        await self._soft_stop_server()

        # stop current work task clients
        self._server_is_work.clear()

        # cancel current task work and close connection
        await self._client_connections.close_all()

    async def send_command(
            self,
            command: bytes,
            unit_id: Optional[int] = None,
            imei: Optional[str] = None,
    ) -> int:
        if unit_id and self.authorization:
            conn = self._client_connections.find_by_unit_id(unit_id)
        else:
            conn = self._client_connections.find_by_imei(imei)

        await conn.send_command(command)

    async def _init_client_connection(
            self,
            reader: StreamReader,
            writer: StreamWriter,
            **kwargs
    ):
        unit = Unit(
            protocol=self.protocol,
            authorization=self.authorization
        )
        client_conn = ClientConnection(
            msgs_queue=self._msgs_queue,
            unit=unit,
            connector=TCPReaderWriter(reader=reader, writer=writer),
            server_status=self._server_is_work,
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
