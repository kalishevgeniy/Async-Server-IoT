import pytest
from unittest.mock import AsyncMock, Mock
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

    connection.unit.id = 1
    return connection


def test_add_unregistered_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    assert client_connection in client_connections._unregistered_connections


def test_add_registered_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connections._register_new_connection()
    assert client_connection in client_connections._client_connections.values()


def test_remove_registered_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connections._register_new_connection()
    client_connections.remove(client_connection)
    assert client_connection not in client_connections._client_connections.values()


def test_remove_unregistered_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connections.remove(client_connection)
    assert client_connection not in client_connections._unregistered_connections


def test_find_existing_connection(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connections._register_new_connection()
    found_connection = client_connections.find(client_connection.unit.id)
    assert found_connection == client_connection


def test_find_non_existing_connection_raises_error(client_connections):
    with pytest.raises(UnitNotFount):
        client_connections.find(999)


@pytest.mark.asyncio
async def test_close_all_connections(client_connections, client_connection):
    client_connections.add(client_connection)
    client_connections._register_new_connection()
    client_connection.close_connection = AsyncMock()
    await client_connections.close_all()
    client_connection.close_connection.assert_awaited_once()