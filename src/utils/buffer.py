from typing import Optional

from src.protocol.abstract import AbstractProtocol
from src.utils.config import ServerConfig


class BufferOverflow(Exception):
    """
    Local buffer overflow
    """


class Buffer:

    __slots__ = '_message', '_handler', '_max_buffer_size'

    def __init__(
            self,
            handler: AbstractProtocol,
            config: ServerConfig,
            *args,
            **kwargs
    ):
        self._max_buffer_size = config.local_buffer_size
        self._message = bytes()
        self._handler = handler

    def update(self, bytes_: bytes):
        if len(self._message) > self._max_buffer_size:
            raise BufferOverflow

        self._message += bytes_

    @property
    def is_empty(self) -> bool:
        return not self._message

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
        else:
            self._message = bytes()

    def get_all(self) -> bytes:
        return self._message
