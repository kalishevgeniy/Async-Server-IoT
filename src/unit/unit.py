from typing import Optional

from .buffer import Buffer
from src.protocol.abstract import AbstractProtocol
from src.status.abstract import Status
from src.status.auth import StatusAuth
from src.status.exception import exception_unit_wrapper
from src.status.parsing import StatusParsing
from ..auth.abstract import AbstractAuthorization

import logging

from ..utils.message import Message


class Unit:

    __slots__ = (
        '_handler', '_auth', '_meta', 'imei', 'is_authorized', '_buffer'
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

        self._meta: dict = dict()

    def get_packet(self) -> bytes:
        if self.is_authorized:
            return self._buffer.get_full_packet()
        else:
            return self._buffer.get_full_login_packet()

    def analyze_packet(
            self,
            packet: bytes
    ) -> tuple[Status, Optional[list[Message]]]:
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
            metadata=self._meta,
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
        self._meta = self._handler.parsing_login_packet(login_packet)

        self.imei = self._handler.get_imei(self._meta)

        if self._auth:
            status.authorization = self._auth.authorized_in_system(
                imei=self.imei
            )
            self.is_authorized = status.authorization

            password = self._handler.get_password(self._meta)
            status.password = self._auth.check_password(
                imei=self.imei,
                password=password
            )
        else:
            status.authorization = True
            self.is_authorized = True
            status.password = True

        logging.debug(f"Unit: {self.imei} {status}")

        return status, None

    @exception_unit_wrapper
    def _analyze_data_packet(
            self,
            data_packet: bytes
    ) -> tuple[StatusParsing, list[Message]]:
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

    def update_buffer(self, bytes_: bytes):
        self._buffer.update_buffer(bytes_)
