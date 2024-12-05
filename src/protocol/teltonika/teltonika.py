from typing import Optional

from ..abstract import AbstractProtocol
import struct

from src.status.auth import StatusAuth
from src.status.parsing import StatusParsing
from fastcrc import crc16
from itertools import islice

import logging

from ..interface import MessageAnnotated
from ...utils.message import LoginMessage
from ...utils.meta import MetaData


def batched(iterable, n):
    """Batch data into lists of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be >= 1')
    it = iter(iterable)
    while batch := list(islice(it, n)):
        yield batch


class Teltonika(AbstractProtocol):
    START_BIT_LOGIN = b'\x00'
    START_BIT_PACKET = b'\x00\x00\x00\x00'

    def __str__(self):
        return 'Teltonika'

    def custom_start_end_login(self, data: bytes) -> tuple[int, int]:
        return 2, struct.unpack('>H', data[:2])[0] + 2

    def custom_start_end_packet(self, data: bytes) -> tuple[int, int]:
        return 4, 12 + struct.unpack('>L', data[4:8])[0]

    def parsing_login_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> LoginMessage:
        return LoginMessage(
            imei=bytes_.decode(),
        )

    def answer_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> bytes:
        return b'\x01'

    def answer_failed_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData,
    ) -> Optional[bytes]:
        return b'\x00'

    def check_crc_data(
            self,
            bytes_: bytes,
            meta: MetaData,
    ) -> bool:
        return (
                crc16.arc(bytes_[4:-4])
                ==
                struct.unpack('>L', bytes_[-4:])[0]
        )

    def parsing_packet(
            self,
            bytes_data: bytes,
            meta: MetaData,
    ) -> MessageAnnotated:

        len_packet = len(bytes_data) - 11
        codec_id, number_data_1, number_data_2 = struct.unpack(
            f'>4x2B{len_packet}x1s4x', bytes_data
        )
        meta.all_count_packet = number_data_2

        match codec_id:
            case 0x08:
                packets = self._parsing_codec_8(bytes_data[6:-5])
            case 0x8e:
                packets = self._parsing_codec_8e(bytes_data[6:-5])
            case _:
                logging.debug("Warning, unknown codec_id!")
                packets = list()

        return packets

    @staticmethod
    def _get_len_packets(bytes_data: bytes) -> int:
        return struct.unpack('B', bytes_data[0:1])[0]

    @staticmethod
    def _get_name_value(
            bd: bytes,
            struct_str: str,
            len_sub_packet: int,
            packet_name: str = 'B'
    ) -> dict:
        batch = batched(
            struct.unpack(
                f">{len_sub_packet * f'{packet_name}{struct_str}'}",
                bd
            ),
            n=2
        )
        return dict(batch)

    def _parsing_codec_8(self, bytes_data: bytes) -> list[dict]:
        packets_return = list()

        while bytes_data:
            packet = dict()

            _time, priority = struct.unpack('>QB', bytes_data[:9])
            lon, lat, alt, angle, sats, speed = self._gps_data(bytes_data[9:24])

            event_io_id, n_total_id = struct.unpack('>2B', bytes_data[24:26])
            bytes_data = bytes_data[26:]
            len_value = 1

            for _ in range(4):
                len_sub_p = bytes_data[0]
                dict_values = self._get_name_value(
                    bd=bytes_data[1:1 + len_sub_p + len_sub_p * len_value],
                    struct_str={1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[len_value],
                    len_sub_packet=len_sub_p,
                )
                packet.update(dict_values)

                bytes_data = bytes_data[1 + len_sub_p + len_sub_p * len_value:]

                n_total_id -= len_sub_p
                len_value *= 2

            packet.update(
                {
                    'longitude': lon,
                    'latitude': lat,
                    'altitude': alt,
                    'angle': angle,
                    'satellites': sats,
                    'speed': speed,
                    'time': _time,
                    'priority': priority
                }
            )
            packets_return.append(packet)

        return packets_return

    @staticmethod
    def _gps_data(
            bytes_data: bytes
    ) -> tuple[float, float, int, int, int, int]:
        lon, lat, alt, angle, sats, speed = struct.unpack(
            '>2I2H1B1H',
            bytes_data
        )
        direction = -1 if lat >> 31 else 1
        lat = (lat & 0x7F_FF_FF_FF * direction) / 10_000_000
        lon = (lon & 0x7F_FF_FF_FF * direction) / 10_000_000
        return lon, lat, alt, angle, sats, speed

    def _parsing_codec_8e(self, bytes_data: bytes) -> list[dict]:
        packets_return = list()

        while bytes_data:
            packet = dict()

            _time, priority = struct.unpack('>QB', bytes_data[:9])
            lon, lat, alt, angle, sats, speed = self._gps_data(
                bytes_data[9:24])

            event_io_id, n_total_id = struct.unpack('>2H', bytes_data[24:28])
            bytes_data = bytes_data[28:]
            len_value = 1

            for _ in range(5):

                if len_value > 8:
                    count_extend, = struct.unpack('>H', bytes_data[0:2])
                    bytes_data = bytes_data[2:]
                    while count_extend:
                        name, len_value = struct.unpack('>2H', bytes_data[0:4])

                        packet[name] = bytes_data[4:len_value+4].hex()
                        bytes_data = bytes_data[len_value+4:]
                        count_extend -= 1

                    break

                len_sub_p, = struct.unpack('>H', bytes_data[0:2])
                _len_value = {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[len_value]

                dict_values = self._get_name_value(
                    bd=bytes_data[2:2 + len_sub_p * 2 + len_sub_p * len_value],
                    struct_str=_len_value,
                    len_sub_packet=len_sub_p,
                    packet_name='H'
                )
                packet.update(dict_values)

                bytes_data = bytes_data[2 + len_sub_p * 2 + len_sub_p * len_value:]

                n_total_id -= len_sub_p
                len_value *= 2

            packet.update(
                **{
                    'longitude': lon,
                    'latitude': lat,
                    'altitude': alt,
                    'angle': angle,
                    'satellites': sats,
                    'speed': speed,
                    'time': _time,
                    'priority': priority
                }
            )
            packets_return.append(packet)

        return packets_return

    def answer_packet(
            self,
            status: StatusParsing,
            meta: MetaData
    ) -> Optional[bytes]:
        return b''.join(
            (b'\x00\x00\x00', meta.all_count_packet)
        )

