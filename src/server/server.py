from typing import Type, Optional

from main import ServerFactory
from src.auth.authorization import AbstractAuthorization
from src.protocol.abstract import AbstractProtocol
from src.utils.config import ServerConfig


class IoTServer:
    def __init__(
            self,
            host: str,
            port: int,
            protocol: Type[AbstractProtocol],
            authorization: Optional[AbstractAuthorization] = None,
            *args,
            **kwargs
    ):
        self.config = self._init_server_config(
            port=port,
            host=host,
            **kwargs
        )

        self._server = self._init_server_factory(
            config=self.config,
            protocol=protocol,
            authorization=authorization,
        )
        self._client_connections = set()

    async def __aenter__(self):
        await self._server.run()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def __aiter__(self):
        return self._server.get_msgs_iter()

    async def run(self):
        await self._server.run()

    async def stop(self):
        await self._server.stop()

    def exec_msgs(self):
        return self._server.exec_msgs()

    @staticmethod
    def _init_server_config(
            host: str,
            port: int,
            **kwargs
    ):
        return ServerConfig(
            host=host,
            port=port,
            **kwargs
        )

    @staticmethod
    def _init_server_factory(
            config: ServerConfig,
            protocol: Type[AbstractProtocol],
            authorization: Optional[AbstractAuthorization] = None,
    ):
        return ServerFactory(
            config=config,
            protocol=protocol,
            authorization=authorization,
        )
