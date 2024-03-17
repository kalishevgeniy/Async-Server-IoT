from abc import abstractmethod, ABCMeta
from typing import Optional

from src.status import StatusAuth, StatusException, StatusParsing


class ProtocolInterface(object, metaclass=ABCMeta):

    __slots__ = (
        '_START_BIT_PACKET', '_END_BIT_PACKET',
        '_START_BIT_LOGIN', '_END_BIT_LOGIN',
        '_LEN_LOGIN_PACKET'
    )

    _START_BIT_PACKET: Optional[bytes]
    _END_BIT_PACKET: Optional[bytes]

    _START_BIT_LOGIN: Optional[bytes]
    _END_BIT_LOGIN: Optional[bytes]
    _LEN_LOGIN_PACKET: Optional[int]

    @abstractmethod
    def get_imei(
            self,
            metadata: dict
    ) -> Optional[str]:
        """
        :param metadata:
        :return:
        """

    @abstractmethod
    def get_password(
            self,
            metadata: dict
    ) -> Optional[str]:
        """
        :param metadata:
        :return:
        """

    @abstractmethod
    def parsing_login_packet(
            self,
            bytes_data: bytes
    ) -> dict:
        """
        :param bytes_data:
        :return:
        """

    @abstractmethod
    def answer_login_packet(
            self,
            status: StatusAuth,
            metadata: dict
    ) -> bytes:
        """
        :param status:
        :param metadata:
        :return:
        """

    @abstractmethod
    def parsing_packet(
            self,
            bytes_data: bytes,
            metadata: dict
    ) -> list[dict]:
        """
        :param bytes_data:
        :param metadata:
        :return:
        """

    @abstractmethod
    def answer_failed_login_packet(
            self,
            status: StatusAuth,
            metadata: dict
    ) -> Optional[bytes]:
        """
        :param status:
        :param metadata:
        :return:
        """

    @abstractmethod
    def answer_failed_data_packet(
            self,
            status: StatusParsing,
            metadata: dict
    ) -> Optional[bytes]:
        """
        :param status:
        :param metadata:
        :return:
        """

    @abstractmethod
    def answer_packet(
            self,
            status: StatusParsing,
            metadata: dict
    ) -> Optional[bytes]:
        """
        :param status:
        :param metadata:
        :return:
        """

    @abstractmethod
    def answer_exception(
            self,
            status: StatusException,
            metadata: dict
    ) -> Optional[bytes]:
        """
        :param status:
        :param metadata:
        :return:
        """

    @abstractmethod
    def check_crc_login(self, login_packet: bytes) -> bool:
        """
        :param login_packet:
        :return:
        """

    @abstractmethod
    def check_crc_data(self, data_packet: bytes) -> bool:
        """
        :param data_packet:
        :return:
        """

    @abstractmethod
    def custom_start_end_login(self, data: bytes) -> tuple[int, int]:
        """
        :param data:
        :return:
        """

    def custom_start_end_packet(self, data: bytes) -> tuple[int, int]:
        """
        :param data:
        :return:
        """

    @property
    @abstractmethod
    def start_bit_packet(self) -> Optional[bytes]:
        """
        :return:
        """

    @property
    @abstractmethod
    def end_bit_packet(self) -> Optional[bytes]:
        """
        :return:
        """

    @property
    @abstractmethod
    def start_bit_login(self) -> Optional[bytes]:
        """
        :return:
        """

    @property
    @abstractmethod
    def end_bit_login(self) -> Optional[bytes]:
        """
        :return:
        """

    @property
    @abstractmethod
    def len_login_packet(self) -> Optional[int]:
        """
        :return:
        """