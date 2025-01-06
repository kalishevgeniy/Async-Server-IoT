import asyncio

import pytest
from unittest.mock import AsyncMock, Mock, patch
from asyncio import StreamReader, StreamWriter, Queue
from src.client.connector.tcp import ConnectorTCP


async def fake_read(n):
    await asyncio.sleep(5)


@pytest.fixture
async def stream_reader():
    return Mock(spec=StreamReader, read=fake_read)


@pytest.fixture
def stream_writer():
    return Mock(spec=StreamWriter)


@pytest.fixture
async def connector_tcp(stream_reader, stream_writer):
    connector = ConnectorTCP(stream_reader, stream_writer)
    return connector


@pytest.mark.asyncio
async def test_execute_bytes_with_data(connector_tcp):
    connector_tcp._reader_queue.put_nowait(b'data1')
    connector_tcp._reader_queue.put_nowait(b'data2')
    result = connector_tcp.execute_bytes()
    assert result == b'data1data2'


@pytest.mark.asyncio
async def test_execute_bytes_no_data(connector_tcp):
    result = connector_tcp.execute_bytes()
    assert result == b''


@pytest.mark.asyncio
async def test_is_not_alive_when_task_done(connector_tcp):
    connector_tcp._task_reader.cancel()
    await asyncio.sleep(0)
    assert connector_tcp.is_not_alive is True


def test_is_not_alive_when_task_not_done(connector_tcp):
    assert connector_tcp.is_not_alive is False


def test_new_data_when_queue_not_empty(connector_tcp):
    connector_tcp._reader_queue.put_nowait(b'data')
    assert connector_tcp.new_data is True


def test_new_data_when_queue_empty(connector_tcp):
    assert connector_tcp.new_data is False


def test_get_socket_info(connector_tcp, stream_writer):
    stream_writer.get_extra_info.return_value = 'socket_info'
    result = connector_tcp.get_socket()
    assert result == 'socket_info'


@pytest.mark.asyncio
async def test_close_connection_success(connector_tcp, stream_writer):
    stream_writer.wait_closed = AsyncMock()
    await connector_tcp.close_connection()
    stream_writer.close.assert_called_once()
    stream_writer.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_connection_timeout(connector_tcp, stream_writer):
    stream_writer.wait_closed = AsyncMock(side_effect=asyncio.TimeoutError)
    await connector_tcp.close_connection()
    stream_writer.close.assert_called_once()
    stream_writer.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_data_success(connector_tcp, stream_writer):
    data = b'data'
    stream_writer.drain = AsyncMock()
    await connector_tcp.send(data)
    stream_writer.write.assert_called_once_with(data)
    stream_writer.drain.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_data_when_not_alive(connector_tcp):
    connector_tcp._task_reader.cancel()
    await asyncio.sleep(0)
    with pytest.raises(Exception, match="Connection was closed"):
        await connector_tcp.send(b'data')
