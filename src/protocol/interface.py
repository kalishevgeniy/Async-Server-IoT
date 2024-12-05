from abc import abstractmethod, ABCMeta
from typing import Optional, Union

from src.status import StatusAuth, StatusException, StatusParsing
from src.utils.message import LoginMessage, Message
from src.utils.meta import MetaData

MessageAnnotated = Union[list[Message], Message, None]


class ProtocolInterface(object, metaclass=ABCMeta):

    __slots__ = (
        'START_BIT_PACKET', 'END_BIT_PACKET',
        'START_BIT_LOGIN', 'END_BIT_LOGIN',
        'LEN_LOGIN'
    )

    START_BIT_PACKET: Optional[bytes]
    END_BIT_PACKET: Optional[bytes]
    LEN_PACKET: Optional[int]

    START_BIT_LOGIN: Optional[bytes]
    END_BIT_LOGIN: Optional[bytes]
    LEN_LOGIN: Optional[int]

    @abstractmethod
    def parsing_login_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> LoginMessage:
        """
        :param bytes_:
        :param meta:
        :return: LoginMessage
        """

    @abstractmethod
    def answer_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> Optional[bytes]:
        """
        :param status:
        :param meta:
        :return:
        """

    @abstractmethod
    def parsing_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> MessageAnnotated:
        """
        :param bytes_:
        :param meta:
        :return:
        """

    @abstractmethod
    def answer_failed_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> Optional[bytes]:
        """
        :param status:
        :param meta:
        :return:
        """

    @abstractmethod
    def answer_failed_data_packet(
            self,
            status: StatusParsing,
            meta: MetaData
    ) -> Optional[bytes]:
        """
        :param status:
        :param meta:
        :return:
        """

    @abstractmethod
    def answer_packet(
            self,
            status: StatusParsing,
            meta: MetaData
    ) -> Optional[bytes]:
        """
        :param status:
        :param meta:
        :return:
        """

    @abstractmethod
    def answer_exception(
            self,
            status: StatusException,
            meta: MetaData
    ) -> Optional[bytes]:
        """
        :param status:
        :param meta:
        :return:
        """

    @abstractmethod
    def check_crc_login(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> bool:
        """
        :param bytes_:
        :param meta:
        :return:
        """

    @abstractmethod
    def check_crc_data(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> bool:
        """
        :param bytes_:
        :param meta:
        :return:
        """

    @abstractmethod
    def custom_start_end_login(self, data: bytes) -> tuple[int, int]:
        """
        :param data:
        :return:
        """

    @abstractmethod
    def custom_start_end_packet(self, data: bytes) -> tuple[int, int]:
        """
        :param data:
        :return:
        """

    @abstractmethod
    def create_command(
            self,
            imei: str,
            command: bytes,
            meta: MetaData,
    ) -> bytes:
        """
        Create command for send to device
        :param imei: string imei
        :param command: bytes main body of command
        :param meta:
        :return: ready command for send to device
        """
