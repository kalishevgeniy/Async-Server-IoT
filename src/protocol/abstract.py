from typing import Optional

from src.status import StatusAuth, StatusException, StatusParsing
from .interface import ProtocolInterface
from ..utils.message import PreMessage
from ..utils.meta import MetaData


class AbstractProtocol(ProtocolInterface):

    _START_BIT_PACKET: Optional[bytes] = None
    _END_BIT_PACKET: Optional[bytes] = None

    _START_BIT_LOGIN: Optional[bytes] = None
    _END_BIT_LOGIN: Optional[bytes] = None
    _LEN_LOGIN_PACKET: Optional[int] = None

    def __init__(self):
        self.metadata = MetaData()

    def parsing_login_packet(
            self,
            bytes_data: bytes
    ) -> Optional[list[PreMessage]]:
        raise NotImplementedError

    def answer_failed_login_packet(
            self,
            status: StatusAuth,
    ) -> Optional[bytes]:
        return None

    def answer_failed_data_packet(
            self,
            status: StatusParsing,
    ) -> Optional[bytes]:
        return None

    def answer_login_packet(
            self,
            status: StatusAuth,
    ) -> bytes:
        raise NotImplementedError

    def parsing_packet(
            self,
            bytes_data: bytes,
    ) -> Optional[list[PreMessage]]:
        raise NotImplementedError

    def answer_packet(
            self,
            status: StatusParsing,
    ) -> Optional[bytes]:
        raise NotImplementedError

    def answer_exception(
            self,
            status: StatusException,
    ) -> Optional[bytes]:
        return None

    def get_imei(self) -> Optional[str]:
        raise NotImplementedError

    def get_password(self) -> Optional[str]:
        return None

    def check_crc_login(self, login_packet: bytes) -> bool:
        return True

    def check_crc_data(self, data_packet: bytes) -> bool:
        return True

    def custom_start_end_login(self, data: bytes) -> tuple[int, int]:
        raise NotImplementedError

    def custom_start_end_packet(self, data: bytes) -> tuple[int, int]:
        raise NotImplementedError

    @property
    def start_bit_packet(self) -> Optional[bytes]:
        return self._START_BIT_PACKET

    @property
    def end_bit_packet(self) -> Optional[bytes]:
        return self._END_BIT_PACKET

    @property
    def start_bit_login(self) -> Optional[bytes]:
        return self._START_BIT_LOGIN

    @property
    def end_bit_login(self) -> Optional[bytes]:
        return self._END_BIT_LOGIN

    @property
    def len_login_packet(self) -> Optional[int]:
        return self._LEN_LOGIN_PACKET
