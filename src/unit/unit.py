from typing import Optional

from .buffer import Buffer
from src.protocol.abstract import AbstractProtocol
from src.status.abstract import Status
from src.status.auth import StatusAuth
from src.status.exception import exception_unit_wrapper
from src.status.parsing import StatusParsing
from ..auth.abstract import AbstractAuthorization

import logging

from ..utils.message import PreMessage


class Unit:

    __slots__ = (
        '_handler', '_auth', 'imei', 'is_authorized', '_buffer'
    )

    def __init__(
            self,
            protocol: AbstractProtocol,
            authorization: Optional[AbstractAuthorization],
            *args,
            **kwargs
    ):
        self._buffer = Buffer(handler=protocol, *args, **kwargs)

        self._handler: AbstractProtocol = protocol
        self._auth = authorization

        self.imei = None
        self.is_authorized = False

    def get_packet(self) -> bytes:
        if self.is_authorized:
            return self._buffer.get_full_packet()
        else:
            return self._buffer.get_full_login_packet()

    def analyze_packet(
            self,
            packet: bytes
    ) -> tuple[Status, Optional[list[PreMessage]]]:
        """
        Entry point for analyze packet
        :param packet: bytes
        :return: tuple[Status, Optional[list[dict]]
        """
        if self.is_authorized:
            return self._analyze_data_packet(packet)
        else:
            return self._analyze_login_packet(packet)

    def create_answer(
            self,
            status: Status
    ) -> Optional[bytes]:
        return status.make_answer(
            handler=self._handler
        )

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
        packets = self._handler.parsing_login_packet(login_packet)

        self.imei = self._handler.get_imei()

        if self._auth:
            status.authorization = self._auth.authorized_in_system(
                imei=self.imei
            )
            self.is_authorized = status.authorization

            password = self._handler.get_password()
            status.password = self._auth.check_password(
                imei=self.imei,
                password=password
            )
        else:
            status.authorization = True
            self.is_authorized = True
            status.password = True

        logging.debug(f"Unit: {self.imei} {status}")

        return status, packets

    @exception_unit_wrapper
    def _analyze_data_packet(
            self,
            data_packet: bytes
    ) -> tuple[StatusParsing, list[PreMessage]]:
        """
        Analyze data packet
        Packet parsed by protocol_handler
        :param data_packet:  bytes
        :return:  tuple[StatusParsing, Optional[list[PreMessage]]]
        """

        status = StatusParsing()
        status.crc = self._handler.check_crc_data(data_packet)

        packets = self._handler.parsing_packet(data_packet)

        return status, packets

    def update_buffer(self, bytes_: bytes):
        self._buffer.update_buffer(bytes_)

    def create_command(self, command, **kwargs) -> bytes:
        return self._handler.create_command(
            command=command,
            imei=self.imei,
            **kwargs
        )
