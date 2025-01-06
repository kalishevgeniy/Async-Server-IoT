import pytest
from src.utils.buffer import Buffer, BufferOverflow
from src.protocol.abstract import AbstractProtocol
from src.utils.config import ServerConfig


class MockProtocol(AbstractProtocol):
    pass


def test_buffer_initialization_sets_correct_values():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    assert buffer._max_buffer_size == 1024
    assert buffer._message == bytearray()
    assert not buffer._is_not_empty


def test_update_adds_bytes_to_buffer():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    buffer.update(b"data")
    assert buffer._message == b"data"
    assert buffer._is_not_empty


def test_update_raises_buffer_overflow():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    buffer._message = bytearray(b"a" * 1025)
    with pytest.raises(BufferOverflow):
        buffer.update(b"data")


def test_clear_removes_specified_length():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    buffer.update(b"data")
    buffer.clear(2)
    assert buffer._message == b"ta"
    assert buffer._is_not_empty


def test_clear_removes_all_data():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    buffer.update(b"data")
    buffer.clear()
    assert buffer._message == bytearray()
    assert not buffer._is_not_empty


def test_get_all_returns_all_data():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    buffer.update(b"data")
    assert buffer.get_all() == b"data"


def test_is_not_empty_property_returns_correct_value():
    handler = MockProtocol()
    config = ServerConfig(host="127.0.0.1", port=1883, local_buffer_size=1024)
    buffer = Buffer(handler, config)
    assert not buffer.is_not_empty
    buffer.update(b"data")
    assert buffer.is_not_empty
