import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from src.protocol.interface import MessageAnnotated
from src.server.tcp import TCPServer
from src.status import StatusAuth
from src.utils.config import ServerConfig
from src.protocol.abstract import AbstractProtocol
from src.auth.abstract import AbstractAuthorization
from src.utils.message import LoginMessage, Message
from src.utils.unit import Unit


mock_model = Mock(spec=Message)
mock_model.navigation = Mock()
mock_model.lbs = Mock()
mock_model.parameters = Mock()


class Protocol(AbstractProtocol):

    START_BIT_LOGIN = b'start'
    END_BIT_LOGIN = b'end'
    LEN_LOGIN = None

    def parsing_login_packet(self, bytes_: bytes, unit: Unit) -> LoginMessage:
        return LoginMessage(
            imei="8877665544332211",
        )

    def parsing_packet(self, bytes_: bytes, unit: Unit) -> MessageAnnotated:
        return [mock_model]

    def answer_login_packet(
            self,
            status: StatusAuth,
            unit: Unit,
    ) -> bytes:
        return b"answer"


@pytest.mark.asyncio
async def test_open_tcp_connection():
    config = ServerConfig(host="127.0.0.1", port=8888)

    server = TCPServer(config, Protocol(), Mock(AbstractAuthorization))

    # Start the server
    await server.run()
    assert server._server_is_work.is_set()

    # Simulate a client connection
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    assert writer is not None
    assert not writer.is_closing()

    writer.write(b"start_test_end")
    await writer.drain()
    assert await reader.read(10) == b"answer"

    # Stop the server
    await server.stop()
    assert not server._server_is_work.is_set()
    assert reader.at_eof()

    with pytest.raises(ConnectionRefusedError):
        _, _ = await asyncio.open_connection(
            '127.0.0.1', 8888
        )

    await server.stop()
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_tcp_sending_command():
    config = ServerConfig(host="127.0.0.1", port=8888)
    protocol = Mock(AbstractProtocol)
    authorization = Mock(AbstractAuthorization)
    server = TCPServer(config, protocol, authorization)

    # Start the server
    await server.run()
    assert server._server_is_work.is_set()

    # Simulate a client connection
    _, _ = await asyncio.open_connection('127.0.0.1', 8888)

    # Send a command
    command = b"command"
    unit_id = 1

    server._client_connections.find = Mock(
        return_value=Mock(send_command=AsyncMock(return_value=b"command"))
    )
    response = await server.send_command(command, unit_id)
    assert response == command

    await server.stop()
    await asyncio.sleep(0.1)
