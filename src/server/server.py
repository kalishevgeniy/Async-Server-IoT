import logging
from typing import Optional, Type

from src.auth.abstract import AbstractAuthorization
from src.protocol.abstract import AbstractProtocol

from src.server.intraface import ServerInterface
from src.server.tcp import TCPServer
from src.utils.config import ServerConfig

from contextlib import asynccontextmanager


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


@asynccontextmanager
async def run_server(
        host: str,
        port: int,
        protocol: Type[AbstractProtocol],
        server: Optional[ServerInterface] = None,
        authorization: Optional[AbstractAuthorization] = None,
):
    config: ServerConfig = _init_server_config(
        port=port,
        host=host,
    )

    if not server:
        logging.info('Warning! Start default TCP server')
        server = TCPServer

    _server = server(
        config=config,
        protocol=protocol(),
        authorization=authorization,
    )
    await _server.run()
    try:
        yield _server
    finally:
        await _server.stop()
