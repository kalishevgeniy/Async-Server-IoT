from typing import Optional

from ..protocol.abstract import AbstractProtocol
from ..status.abstract import Status
from ..status.auth import StatusAuth
from ..status.except_status import StatusException, exception_unit_wrapper
from ..status.parsing import StatusParsing
from ..unit.buffer import BufferMixin


class UnitCommunication(BufferMixin):

    __slots__ = (
        '_handler',
        '_is_authorized', '_imei',
        '_pass', '_meta'
    )

    def __init__(self, protocol_handler, *args, **kwargs):
        super().__init__(protocol_handler, *args, **kwargs)
        self._handler: AbstractProtocol = protocol_handler

        self._is_authorized: bool = False
        self._imei: Optional[str] = None
        self._pass: Optional[str] = None
        self._meta: dict = dict()

    @property
    def get_imei(self):
        return self._imei

    def get_packet(self) -> bytes:
        if self._is_authorized:
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
        if self._is_authorized:
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

        self._imei = self._handler.get_imei(self._meta)
        status.authorization = self._authorized_in_system()
        print(f"Unit: {self._imei} Auth status {status.authorization}")

        self._pass = self._handler.get_password(self._meta)
        status.password = self._check_password()

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

    def _authorized_in_system(self) -> bool:
        """
        method to check unit in the system for message with login packet
        for connection with imei in all message need use another method
        :return: bool (True - unit in system, False - unit not in system)
        """
        self._is_authorized = True
        return self._is_authorized

    def _check_password(self) -> bool:
        """
        Check password unit
        :return:
        """
        self._pass = True
        return self._pass
