from typing import Optional

from src.status import StatusAuth, StatusException, StatusParsing
from .interface import ProtocolInterface, MessageAnnotated
from ..utils.message import LoginMessage
from ..utils.unit import Unit


class AbstractProtocol(ProtocolInterface):

    START_BIT_PACKET: Optional[bytes] = None
    END_BIT_PACKET: Optional[bytes] = None
    LEN_PACKET: Optional[int] = None

    START_BIT_LOGIN: Optional[bytes] = None
    END_BIT_LOGIN: Optional[bytes] = None
    LEN_LOGIN: Optional[int] = None

    TYPE: Optional[str] = None

    def parsing_login_packet(
            self,
            bytes_: bytes,
            unit: Unit,
    ) -> LoginMessage:
        raise NotImplementedError

    def answer_failed_login_packet(
            self,
            status: StatusAuth,
            unit: Unit,
    ) -> Optional[bytes]:
        return None

    def answer_failed_data_packet(
            self,
            status: StatusParsing,
            unit: Unit,
    ) -> Optional[bytes]:
        return None

    def answer_login_packet(
            self,
            status: StatusAuth,
            unit: Unit,
    ) -> bytes:
        raise NotImplementedError

    def parsing_packet(
            self,
            bytes_: bytes,
            unit: Unit,
    ) -> MessageAnnotated:
        raise NotImplementedError

    def answer_packet(
            self,
            status: StatusParsing,
            unit: Unit,
    ) -> Optional[bytes]:
        raise NotImplementedError

    def answer_exception(
            self,
            status: StatusException,
            unit: Unit,
    ) -> Optional[bytes]:
        return None

    def check_crc_login(
            self,
            bytes_: bytes,
            unit: Unit,
    ) -> bool:
        return True

    def check_crc_data(
            self,
            bytes_: bytes,
            unit: Unit,
    ) -> bool:
        return True

    def custom_start_end_login(
            self,
            bytes_: bytes
    ) -> tuple[int, int]:
        raise NotImplementedError

    def custom_start_end_packet(
            self,
            bytes_: bytes
    ) -> tuple[int, int]:
        raise NotImplementedError

    def create_command(
            self,
            command: bytes,
            unit: Unit,
    ) -> bytes:
        return command
