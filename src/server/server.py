import logging
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.protocol.abstract import AbstractProtocol

from src.server.intraface import ServerInterface
from src.server.tcp import TCPServer
from src.utils.config import ServerConfig


class IoTServer:
    def __init__(
            self,
            host: str,
            port: int,
            protocol: AbstractProtocol,
            server: Optional[ServerInterface] = None,
            authorization: Optional[AbstractAuthorization] = None,
            *args,
            **kwargs
    ):
        # init config for server runner
        self.config: ServerConfig = self._init_server_config(
            port=port,
            host=host,
            **kwargs
        )

        # init server
        self._server = self._init_server_factory(
            config=self.config,
            server=server,
            protocol=protocol,
            authorization=authorization,
        )

    async def __aenter__(self):
        await self._server.run()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def run(self):
        await self._server.run()

    async def stop(self):
        await self._server.stop()

    def exec_msgs(self, count=-1):
        return self._server.exec_msgs(count)

    @staticmethod
    def _init_server_config(
            host: str,
            port: int,
            **kwargs
    ) -> ServerConfig:
        return ServerConfig(
            host=host,
            port=port,
            **kwargs
        )

    @staticmethod
    def _init_server_factory(
            config: ServerConfig,
            server: Optional[ServerInterface],
            protocol: AbstractProtocol,
            authorization: Optional[AbstractAuthorization] = None,
    ) -> ServerInterface:
        if not server:
            logging.info('Warning! Start default TCP server')
            server = TCPServer

        return server(
            config=config,
            protocol=protocol,
            authorization=authorization,
        )
