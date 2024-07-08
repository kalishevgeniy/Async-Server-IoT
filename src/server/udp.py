import asyncio
from asyncio import Server
from typing import Optional

from src.auth.abstract import AbstractAuthorization
from src.client.connection import ClientConnection
from src.protocol.abstract import AbstractProtocol
from src.server.intraface import ServerInterface
from src.utils.config import ServerConfig

import logging


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

    def exec_msgs(self):
        pass

    async def run(self):
        pass

    async def stop(self):
        pass
