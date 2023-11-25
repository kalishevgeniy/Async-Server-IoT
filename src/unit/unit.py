from typing import Optional

from .buffer import BufferMixin
from src.protocol.abstract import AbstractProtocol
from src.status.abstract import Status
from src.status.auth import StatusAuth
from src.status.except_status import StatusException, exception_unit_wrapper
from src.status.parsing import StatusParsing
from src.auth.authorization import Auth


class UnitCommunication(BufferMixin):

    __slots__ = '_handler', '_auth', '_meta'

    def __init__(self, protocol_handler, *args, **kwargs):
        super().__init__(protocol_handler, *args, **kwargs)
        self._handler: AbstractProtocol = protocol_handler

        self._auth = Auth()
        self._meta: dict = dict()

    @property
    def imei(self):
        return self._auth.imei

    def get_packet(self) -> bytes:
        if self._auth.is_authorized:
            return self.get_full_data_packet()
        else:
            return self.get_full_data_login_packet()

    def analyze_packet(
            self,
            packet: bytes
    ) -> tuple[Status, Optional[list[dict]]]:
        """
        Entry point for analyze packet
        :param packet: bytes
        :return: tuple[Status, Optional[list[dict]]
        """
        if self._auth.is_authorized:
            return self._analyze_data_packet(packet)
        else:
            return self._analyze_login_packet(packet)

    def create_answer_failed(
            self,
            status: Status
    ) -> Optional[bytes]:
        """
        Entry point for making failed answer
        By the status make choice for method failed answer
        :param status: Status (Base class of all type of status)
        :return: Optional[bytes]
        """
        if isinstance(status, StatusAuth):
            return self._handler.answer_failed_login_packet(status, self._meta)
        elif isinstance(status, StatusParsing):
            return self._handler.answer_failed_data_packet(status, self._meta)
        elif isinstance(status, StatusException):
            return self._handler.answer_exception(status, self._meta)
        else:
            raise Exception("Unknown type status")

    def create_answer(
            self,
            status: Status
    ) -> Optional[bytes]:
        if isinstance(status, StatusParsing):
            return self._handler.answer_packet(status, self._meta)
        elif isinstance(status, StatusAuth):
            return self._handler.answer_login_packet(status, self._meta)
        elif isinstance(status, StatusException):
            return self._handler.answer_exception(status, self._meta)
        else:
            raise Exception("Unknown type answer")

    @exception_unit_wrapper
    def _analyze_login_packet(
            self,
            login_packet: bytes
    ) -> tuple[StatusAuth, None]:
        """
        Make parsing login packet
        Check unit is register in system
        :param login_packet: bytes
        :return: tuple[StatusAuth, None]
        """

        status = StatusAuth()

        status.crc = self._handler.check_crc_login(login_packet)
        self._meta = self._handler.parsing_login_packet(login_packet)

        imei = self._handler.get_imei(self._meta)
        status.authorization = self._auth.authorized_in_system(imei)
        print(f"Unit: {imei} Auth status {status.authorization}")

        password = self._handler.get_password(self._meta)
        status.password = self._auth.check_password(imei, password)

        return status, None

    @exception_unit_wrapper
    def _analyze_data_packet(
            self,
            data_packet: bytes
    ) -> tuple[StatusParsing, Optional[list[dict]]]:
        """
        Analyze data packet
        Packet parsed by protocol_handler
        :param data_packet:  bytes
        :return:  tuple[StatusParsing, Optional[list[dict]]]
        """

        status = StatusParsing()
        status.crc = self._handler.check_crc_data(data_packet)

        packets, self._meta = self._handler.parsing_packet(
            data_packet,
            self._meta
        )

        return status, packets
