import logging
from typing import Type, AsyncIterator

from pydantic import IPvAnyAddress

from src.auth.abstract import AbstractAuthorization
from src.protocol.abstract import AbstractProtocol
from src.server.abstract import ServerAbstract

from src.server.tcp import TCPServer
from src.utils.config import ServerConfig

from contextlib import asynccontextmanager


def _init_server_config(
        host: IPvAnyAddress,
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
        host: IPvAnyAddress,
        port: int,
        protocol: Type[AbstractProtocol],
        authorization: AbstractAuthorization,
        server: Type[ServerAbstract] = TCPServer,
) -> AsyncIterator[ServerAbstract]:
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
    try:
        await _server.run()
        yield _server
    finally:
        await _server.stop()
