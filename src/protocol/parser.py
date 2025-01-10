from typing import Callable, Optional

from src.protocol.abstract import AbstractProtocol
from dataclasses import dataclass, field

from src.protocol.interface import MessageAnnotated
from src.status import StatusAuth, exception_wrapper, StatusParsing
from src.status.abstract import Status
from src.utils.buffer import Buffer
from src.utils.message import LoginMessage
from src.utils.unit import Unit


@dataclass
class SizeCleaner:
    need_clear: bool = field(default=True)
    clear_start: int = field(default=0)
    clear_end: int = field(default=-1)
    start: int = field(default=-1)
    end: int = field(default=-0)


class PacketParser:
    def __init__(self, protocol: AbstractProtocol):
        self._p = protocol

        self._login = self.__get_login_parser()
        self._packet = self.__get_packet_parser()

    def __repr__(self):
        return f"<Packet parser ({self._p.TYPE})>"

    def __get_login_parser(self) -> Callable[[bytes], SizeCleaner]:
        return self.__get_parser(
            start=self._p.START_BIT_LOGIN,
            end=self._p.END_BIT_LOGIN,
            len_=self._p.LEN_LOGIN,
            custom=self._p.custom_start_end_login
        )

    def __get_packet_parser(self) -> Callable[[bytes], SizeCleaner]:
        return self.__get_parser(
            start=self._p.START_BIT_PACKET,
            end=self._p.END_BIT_PACKET,
            len_=self._p.LEN_PACKET,
            custom=self._p.custom_start_end_packet
        )

    def __get_parser(
            self,
            custom: Callable,
            len_: Optional[int] = None,
            start: Optional[bytes] = None,
            end: Optional[bytes] = None,
    ) -> Callable[[bytes], SizeCleaner]:
        if start and end and len_:
            return self.__start_end_len(
                start=start,
                end=end,
                len_=len_
            )
        elif start and end:
            return self.__start_end(
                start=start,
                end=end,
            )
        else:
            return custom

    @staticmethod
    def __start_end_len(
            start: bytes,
            end: bytes,
            len_: int
    ) -> Callable[[bytes], SizeCleaner]:
        START = start
        END = end
        LEN = len_

        def func(bytes_: bytes) -> SizeCleaner:
            start_ = 0
            while True:

                if not bytes_.startswith(START, start_):
                    index = bytes_.find(START, start_)

                    if index == -1:
                        return SizeCleaner(
                            need_clear=True
                        )
                    else:
                        start_ += index
                        continue

                if len(bytes_[start_:]) < LEN:
                    return SizeCleaner(
                        need_clear=True,
                        clear_end=start_,
                    )

                s = start_ + LEN
                full = s + len(END)
                if bytes_[s:full] == END:
                    return SizeCleaner(
                        need_clear=True,
                        clear_end=full,
                        start=start_,
                        end=full,
                    )
                else:
                    return SizeCleaner(
                        need_clear=True,
                        clear_end=full,
                    )

        return func

    @staticmethod
    def __start_end(
            start: bytes,
            end: bytes,
    ) -> Callable[[bytes], SizeCleaner]:
        START = start
        END = end

        def func(bytes_: bytes) -> SizeCleaner:
            start_ = 0
            end_ = 0
            while True:

                if not bytes_.startswith(START, start_):
                    index = bytes_.find(START, start_)

                    if index == -1:
                        return SizeCleaner(need_clear=True)
                    else:
                        start_ += index
                        end_ += index
                        continue

                index = bytes_.find(END, start_)

                if index == -1:
                    return SizeCleaner(
                        need_clear=True,
                        clear_end=start_,
                    )

                packet_len = len(bytes_[:index + len(END)])
                return SizeCleaner(
                    need_clear=True,
                    clear_end=packet_len,
                    start=start_,
                    end=packet_len,
                )

        return func

    @exception_wrapper
    def parsing(
            self,
            buffer: Buffer,
            unit: Unit,
    ) -> Optional[tuple[Status, MessageAnnotated, bytes]]:

        bytes_ = buffer.get_all()
        if unit.is_authorized:
            packet_size = self._packet(bytes_)
        else:
            packet_size = self._login(bytes_)

        if packet_size.need_clear:
            buffer.clear(packet_size.clear_end)

        bytes_ = bytes_[packet_size.start:packet_size.end]

        if not bytes_:
            return None

        if unit.is_authorized:
            status, messages = self._analyze_data_packet(
                data_packet=bytes_,
                protocol=self._p,
                unit=unit,
            )
            return status, messages, bytes_
        else:
            status, login_packet = self._analyze_login_packet(
                login_packet=bytes_,
                protocol=self._p,
                unit=unit,
            )
            unit.imei = login_packet.imei
            unit.password = login_packet.password

            return status, login_packet.messages, bytes_

    @staticmethod
    def _analyze_login_packet(
            login_packet: bytes,
            protocol: AbstractProtocol,
            unit: Unit,
    ) -> tuple[StatusAuth, LoginMessage]:
        crc = protocol.check_crc_login(
            login_packet,
            unit=unit,
        )
        packets = protocol.parsing_login_packet(
            login_packet,
            unit=unit,
        )

        return StatusAuth(crc=crc), packets

    @staticmethod
    def _analyze_data_packet(
            data_packet: bytes,
            protocol: AbstractProtocol,
            unit: Unit,
    ) -> tuple[StatusParsing, MessageAnnotated]:
        crc = protocol.check_crc_data(
            data_packet,
            unit=unit
        )
        packets = protocol.parsing_packet(
            data_packet,
            unit=unit
        )

        return StatusParsing(crc=crc), packets
