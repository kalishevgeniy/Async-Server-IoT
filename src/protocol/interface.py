from abc import abstractmethod, ABCMeta
from typing import Optional, Any

from src.status import StatusAuth, StatusException, StatusParsing
from src.utils.message import PreMessage


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
            self
    ) -> Optional[str]:
        """
        :return:
        """

    @abstractmethod
    def get_password(
            self
    ) -> Optional[str]:
        """
        :return:
        """

    @abstractmethod
    def parsing_login_packet(
            self,
            bytes_data: bytes
    ) -> Optional[list[PreMessage]]:
        """
        :param bytes_data:
        :return:
        """

    @abstractmethod
    def answer_login_packet(
            self,
            status: StatusAuth,
    ) -> Optional[bytes]:
        """
        :param status:
        :return:
        """

    @abstractmethod
    def parsing_packet(
            self,
            bytes_data: bytes,
    ) -> Optional[list[PreMessage]]:
        """
        :param bytes_data:
        :return:
        """

    @abstractmethod
    def answer_failed_login_packet(
            self,
            status: StatusAuth,
    ) -> Optional[bytes]:
        """
        :param status:
        :return:
        """

    @abstractmethod
    def answer_failed_data_packet(
            self,
            status: StatusParsing,
    ) -> Optional[bytes]:
        """
        :param status:
        :return:
        """

    @abstractmethod
    def answer_packet(
            self,
            status: StatusParsing,
    ) -> Optional[bytes]:
        """
        :param status:
        :return:
        """

    @abstractmethod
    def answer_exception(
            self,
            status: StatusException,
    ) -> Optional[bytes]:
        """
        :param status:
        :return:
        """

    @abstractmethod
    def check_crc_login(
            self,
            login_packet: bytes
    ) -> bool:
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

    @abstractmethod
    def custom_start_end_packet(self, data: bytes) -> tuple[int, int]:
        """
        :param data:
        :return:
        """

    def create_command(
            self,
            imei: str,
            command: bytes,
            **kwargs: dict[Any, Any]
    ) -> bytes:
        """
        Create command for send to device
        :param imei: string imei
        :param command: bytes main body of command
        :param kwargs: extra parameters
        :return: ready command for send to device
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