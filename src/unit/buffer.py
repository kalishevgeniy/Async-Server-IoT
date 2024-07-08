from typing import Optional
from src.protocol.abstract import AbstractProtocol


class Buffer:

    __slots__ = '_message', '_handler', '_max_buffer_size'

    def __init__(self, handler, *args, **kwargs):
        self._max_buffer_size = 65536   # todo add setting
        self._message: bytes = bytes()
        self._handler: AbstractProtocol = handler

    def update_buffer(self, bytes_: bytes):
        if len(self._message) > self._max_buffer_size:
            raise Exception  # todo add custom exception

        self._message += bytes_

    @property
    def is_empty(self) -> bool:
        return not self._message

    def clear_buffer(
            self,
            len_to_clear: int = None
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

    def get_full_login_packet(self) -> Optional[bytes]:
        """
        Get correct login packet, using ProtocolHandler
        Clear buffer if data incorrect
        :return: Optional[bytes] (login packet)
        """
        start_bl = self._handler.start_bit_login
        end_bl = self._handler.end_bit_login

        if not start_bl or not end_bl:
            start, end = self._handler.custom_start_end_login(self._message)

            message_return = self._message[start:end]
            self.clear_buffer(end)

            return message_return

        elif len_lp := self._handler.len_login_packet:
            if (
                    self._message.startswith(start_bl)
                    and
                    self._message[:len_lp].endswith(end_bl)
            ):
                message_return = self._message[:len_lp]
                self.clear_buffer(len_lp)
                return message_return

        else:
            start = self._message.find(start_bl)
            end = self._message.find(end_bl)

            if -1 not in (start, end):
                end = end+len(end_bl)

                message_return = self._message[start:end]
                self.clear_buffer(end)
                return message_return

        self.clear_buffer()
        return None

    def get_full_packet(self) -> Optional[bytes]:
        if not self._message:
            return None

        start_bp = self._handler.start_bit_packet
        end_bp = self._handler.end_bit_packet

        if start_bp and end_bp:
            start = self._message.find(start_bp)
            end = self._message.find(end_bp)

            if start >= 0 and end > 0:

                end = end + len(end_bp)
                if len(self._message) < end:
                    return None

                message = self._message[start:end]
                self.clear_buffer(end)
                return message
            else:
                return bytes()

        else:
            start, end = self._handler.custom_start_end_packet(
                data=self._message
            )

            if len(self._message) < end:
                return None

            message_return = self._message[start:end]
            self.clear_buffer(end)

            return message_return
