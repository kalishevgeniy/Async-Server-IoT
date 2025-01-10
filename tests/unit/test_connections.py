import pytest
from unittest.mock import AsyncMock, Mock

from src.auth.abstract import AbstractAuthorization
from src.client.connections.connections import ClientConnections, UnitNotFount
from src.client.connections.connection import ClientConnection
from src.utils.unit import Unit


@pytest.fixture
def client_connections():
    return ClientConnections()


@pytest.fixture
def client_connection():
    connection = Mock(spec=ClientConnection)
    connection.unit = Mock(Unit)
    connection.authorization = Mock(AbstractAuthorization)

    connection.unit.id = 1
    return connection


def test_add_unregistered_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    assert client_connection in client_connections._unregistered_connections


@pytest.mark.asyncio
async def test_remove_registered_connection(client_connections, client_connection):
    client_connection.authorization.authorized_in_system = AsyncMock(return_value=1)
    client_connections.add(client_connection)
    await client_connection.authorization.authorized_in_system()
    client_connections.remove(client_connection)
    assert client_connection not in client_connections._client_connections.values()


@pytest.mark.asyncio
async def test_add_connection_to_registered(client_connections, client_connection):
    client_connection.authorization.authorized_in_system = AsyncMock(return_value=1)
    client_connections.add(client_connection)
    await client_connection.authorization.authorized_in_system()
    assert client_connection in client_connections._client_connections.values()


def test_remove_unregistered_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connections.remove(client_connection)
    assert client_connection not in client_connections._unregistered_connections


@pytest.mark.asyncio
async def test_find_existing_connection(client_connections, client_connection):
    client_connection.authorization.authorized_in_system = AsyncMock(return_value=1)
    client_connections.add(client_connection)
    await client_connection.authorization.authorized_in_system()
    found_connection = client_connections.find(1)
    assert found_connection == client_connection


def test_find_non_existing_connection_raises_error(client_connections):
    with pytest.raises(UnitNotFount):
        client_connections.find(999)


@pytest.mark.asyncio
async def test_close_all_connections(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connection.close_connection = AsyncMock()
    await client_connections.close_all()
    client_connection.close_connection.assert_awaited_once()
