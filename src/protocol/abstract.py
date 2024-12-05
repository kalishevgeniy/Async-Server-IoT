from typing import Optional, Any
from venv import logger

from src.status import StatusAuth, StatusException, StatusParsing
from .interface import ProtocolInterface, MessageAnnotated
from ..utils.message import LoginMessage
from ..utils.meta import MetaData


class AbstractProtocol(ProtocolInterface):

    START_BIT_PACKET: Optional[bytes] = None
    END_BIT_PACKET: Optional[bytes] = None
    LEN_PACKET: Optional[int] = None

    START_BIT_LOGIN: Optional[bytes] = None
    END_BIT_LOGIN: Optional[bytes] = None
    LEN_LOGIN: Optional[int] = None

    def parsing_login_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> LoginMessage:
        raise NotImplementedError

    def answer_failed_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> Optional[bytes]:
        return None

    def answer_failed_data_packet(
            self,
            status: StatusParsing,
            meta: MetaData
    ) -> Optional[bytes]:
        return None

    def answer_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> bytes:
        raise NotImplementedError

    def parsing_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> MessageAnnotated:
        raise NotImplementedError

    def answer_packet(
            self,
            status: StatusParsing,
            meta: MetaData
    ) -> Optional[bytes]:
        raise NotImplementedError

    def answer_exception(
            self,
            status: StatusException,
            meta: MetaData
    ) -> Optional[bytes]:
        return None

    def check_crc_login(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> bool:
        return True

    def check_crc_data(
            self,
            bytes_: bytes,
            meta: MetaData
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
            imei: str,
            command: bytes,
            meta: MetaData,
    ) -> bytes:
        logger.debug(
            f"Send default command to object {imei}"
            f" with command {command.decode()}"
        )
        return command
