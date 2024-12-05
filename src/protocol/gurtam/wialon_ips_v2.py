from datetime import datetime
from typing import Optional

from fastcrc import crc16

from src.protocol.abstract import AbstractProtocol
from src.protocol.interface import MessageAnnotated
from src.status.auth import StatusAuth
from src.status.parsing import StatusParsing
from src.utils.message import Message, LoginMessage, Navigation, LBS
from src.utils.meta import MetaData


class WialonIPSv2(AbstractProtocol):
    START_BIT_PACKET: bytes = b'#'
    END_BIT_PACKET: bytes = b'\r\n'

    START_BIT_LOGIN: bytes = b'#L#'
    END_BIT_LOGIN: bytes = END_BIT_PACKET

    _EMPTY = b'NA'

    def __str__(self):
        return 'WialonIPSv2'

    def parsing_login_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> LoginMessage:
        _, _, data = bytes_.split(b'#')
        protocol_version, imei, password, _ = data.split(b';')

        return LoginMessage(
            imei=imei.decode(),
            password=password.decode()
        )

    def create_command(
            self,
            imei: str,
            command: bytes,
            meta: MetaData,
    ) -> bytes:
        return b'%b\r\n' % command

    def check_crc_login(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> bool:
        body = bytes_[3:-6]
        crc = bytes_[-6:-2]
        return int(crc, 16) == crc16.arc(body)

    def check_crc_data(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> bool:
        return self.check_crc_login(bytes_=bytes_, meta=meta)

    def answer_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> bytes:
        return b'#AL#1\r\n'

    def answer_failed_login_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> Optional[bytes]:
        if status.error or status.authorization or status.crc:
            return b'#AL#0\r\n'
        elif status.password:
            return b'#AL#01\r\n'
        elif status.crc:
            return b'#AL#10\r\n'

        return None

    def answer_failed_packet(
            self,
            status: StatusAuth,
            meta: MetaData
    ) -> Optional[bytes]:
        pass

    def answer_packet(
            self,
            status: StatusParsing,
            meta: MetaData
    ) -> Optional[bytes]:
        return b"#A%b#1\r\n" % b'B'

    def parsing_packet(
            self,
            bytes_: bytes,
            meta: MetaData
    ) -> MessageAnnotated:
        _, packet_type, data = bytes_.split(b'#')

        match packet_type:
            case b'D':
                packets = [self._parse_packet_d(data)]
            case b'SD':
                packets = [self._parse_packet_sd(data)]
            case b'B':
                packets = self._parse_packet_b(data)
            case _:
                packets = None

        meta.last_type_packet = packet_type
        return packets

    def _parse_packet_sd(self, bytes_: bytes) -> Message:
        message = self._get_base_data(*bytes_.split(b';', 10))
        return message

    def _parse_packet_d(self, bytes: bytes) -> Message:
        (
            date, _time,
            lat, lat_dir, lon, lon_dir,
            speed, course, alt, sats, hdop,
            inputs, outputs, adc, ibutton, params, _
        ) = bytes.split(b';', 17)

        message = self._get_base_data(
            date, _time,
            lat, lat_dir, lon, lon_dir,
            speed, course, alt, sats
        )

        if hdop := float(hdop) if hdop != self._EMPTY else None:
            message.lbs = LBS(hdop=hdop)

        message.parameters = dict()
        message.parameters.update(**{
            'ibutton': str(ibutton) if ibutton != self._EMPTY else None
        })

        if self._EMPTY != inputs and inputs:
            message.parameters.update(**{
                f"in_{num}": int(val)
                for num, val
                in enumerate(f"{int(inputs):b}"[::-1])
            })

        if self._EMPTY != outputs and outputs:
            message.parameters.update(**{
                f"out_{num}": int(val)
                for num, val
                in enumerate(f"{int(outputs):b}"[::-1])
            })

        if self._EMPTY != adc and adc:
            message.parameters.update(**{
                f"adc_{num}": float(val)
                for num, val
                in enumerate(adc.split(b','))
            })

        if self._EMPTY != params and params:
            list_parameters = list()
            for param in params.split(b","):
                if param:
                    p_name, p_type, p_val = param.split(b":", 2)
                    list_parameters.append(
                        {
                            "name": str(p_name),
                            "type": str(p_type),
                            "value": str(p_val)
                        }
                    )
            message.parameters.update(**{'parameters': list_parameters})
        return message

    def _parse_packet_b(self, bytes_: bytes) -> list[Message]:
        ready_packets = list()

        packets_b = bytes_.split(b'|')
        for packet in packets_b:
            ready_packets.append(self._parse_packet_sd(packet))

        return ready_packets

    def _get_base_data(self, *args) -> Message:
        (
             date, _time,
             lat, lat_dir, lon, lon_dir,
             speed, course, alt, sats
        ) = args

        return Message(
            time_=self._get_time(date, _time),
            navigation=Navigation(
                latitude=self._get_lat(lat, lat_dir),
                longitude=self._get_lon(lon, lon_dir),
                speed=float(speed) if speed != self._EMPTY else 0,
                course=int(course) if course != self._EMPTY else 0,
                altitude=float(alt) if alt != self._EMPTY else 0,
                satellites=int(sats) if sats != self._EMPTY else 0,
            )
        )

    def _get_time(self, date: bytes, time_: bytes) -> datetime:
        if self._EMPTY not in (date, time_):
            return datetime(
                    year=int(date[4:6]) + 2000,
                    month=int(date[2:4]),
                    day=int(date[0:2]),
                    hour=int(time_[0:2]),
                    minute=int(time_[2:4]),
                    second=int(time_[4:6])
                )
        return datetime.now()

    def _get_lat(self, lat: bytes, lat_dir: bytes) -> float:
        if self._EMPTY not in (lat, lat_dir):
            direction = 1 if lat_dir == b'N' else -1
            return (int(lat[:2]) + float(lat[2:]) / 60.) * direction
        return 0.0

    def _get_lon(self, lon: bytes, lon_dir: bytes) -> float:
        if self._EMPTY not in (lon, lon_dir):
            direction = 1 if lon_dir == b'E' else -1
            return (int(lon[:3]) + float(lon[3:])) * direction

        return 0.0
