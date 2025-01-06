from typing import Optional

from src.protocol.abstract import AbstractProtocol
from src.utils.config import ServerConfig


class BufferOverflow(Exception):
    """
    Local buffer overflow
    """


class Buffer:

    __slots__ = (
        '_message', '_handler', '_max_buffer_size', '_is_not_empty'
    )

    def __init__(
            self,
            handler: AbstractProtocol,
            config: ServerConfig,
            *args,
            **kwargs
    ):
        self._max_buffer_size = config.local_buffer_size

        self._message = bytearray()
        self._is_not_empty = False
        self._handler = handler

    def __repr__(self):
        return (
            f"Buffer("
            f"msgs_len={len(self._message)}, "
            f"max_buffer_size={self._max_buffer_size}"
            f")"
        )

    def update(self, bytes_: bytes):
        if len(self._message) > self._max_buffer_size:
            raise BufferOverflow

        self._message.extend(bytes_)
        self._is_not_empty = True

    @property
    def is_not_empty(self) -> bool:
        return self._is_not_empty

    def clear(
            self,
            len_to_clear: Optional[int] = None
    ):
        """
        Make cleaning of data buffer
        :param len_to_clear: int
        :return: None
        """
        if isinstance(len_to_clear, int):
            self._message = self._message[len_to_clear:]

            if not (self._message and len_to_clear > 0):
                self._is_not_empty = False

        else:
            self._is_not_empty = False
            self._message = bytearray()

    def get_all(self) -> bytes:
        return bytes(self._message)
