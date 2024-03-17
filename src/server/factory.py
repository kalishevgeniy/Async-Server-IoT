import asyncio
from asyncio import Server
from typing import Type, Optional

from src.auth.authorization import AbstractAuthorization
from src.client.connection import ClientConnection
from src.protocol.abstract import AbstractProtocol
from src.utils.config import ServerConfig

import logging


class ServerFactory:
    def __init__(
            self,
            config: ServerConfig,
            protocol: Type[AbstractProtocol],
            authorization: Optional[AbstractAuthorization] = None,
    ):
        self.config = config
        self.protocol = protocol()
        self.authorization = authorization

        self._task_server: Optional[Server] = None

        self._server_is_work: asyncio.Event = asyncio.Event()
        self._client_connections: set[ClientConnection] = set()
        self._msgs_queue = asyncio.Queue(config.queue_size)

    async def msgs_iterator(self):
        while True:
            yield await self._msgs_queue.get()

    def exec_msgs(self):
        msgs = list()
        while not self._msgs_queue.empty():
            msgs.append(
                self._msgs_queue.get_nowait()
            )

        return msgs

    async def run(self):
        self._task_server = await asyncio.start_server(
            self._init_client_connection,
            host=str(self.config.host),
            port=self.config.port,
            **self.config.model_extra,
        )
        await self._task_server.start_serving()

        self._server_is_work.set()

    async def _soft_stop_server(self):
        self._task_server.close()
        try:
            await asyncio.wait_for(
                self._task_server.wait_closed(),
                15
            )
        except asyncio.TimeoutError:
            print('Timeout error close socket')

    async def _soft_close_client_connection(self):
        async with asyncio.TaskGroup() as tg:
            for client in self._client_connections:
                tg.create_task(client.close_connection())

        self._client_connections = None

    async def stop(self):
        await self._soft_stop_server()

        # stop current work task clients
        self._server_is_work.clear()

        # cancel current task work and close connection
        await self._soft_close_client_connection()

    async def _init_client_connection(
            self,
            *args,
            **kwargs
    ):
        reader, writer = args
        client_conn = ClientConnection(
            reader=reader,
            writer=writer,
            msgs_queue=self._msgs_queue,
            protocol=self.protocol,
            server_status=self._server_is_work,
            authorization=self.authorization,
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
