from datetime import datetime
from time import time
from typing import Optional, Any

from fastcrc import crc16

from src.protocol.abstract import AbstractProtocol
from src.status.auth import StatusAuth
from src.status.parsing import StatusParsing
from src.utils.message import PreMessage


class WialonIPSv2(AbstractProtocol):
    _START_BIT_PACKET: bytes = b'#'
    _END_BIT_PACKET: bytes = b'\r\n'

    _START_BIT_LOGIN: bytes = b'#L#'
    _END_BIT_LOGIN: bytes = _END_BIT_PACKET

    _EMPTY = b'NA'

    def __str__(self):
        return 'WialonIPSv2'

    def parsing_login_packet(self, bytes_data: bytes) -> list[PreMessage]:
        _, _, data = bytes_data.split(b'#')
        protocol_version, imei, password, _ = data.split(b';')
        self.metadata.imei = imei.decode()

        return [PreMessage(**{'parameters': {
            'imei': imei,
            'protocol_version': protocol_version,
            'password': password
        }})]

    def get_imei(self) -> Optional[str]:
        return self.metadata.imei

    def get_password(self) -> Optional[str]:
        return self.metadata.password

    def create_command(
            self,
            imei: str,
            command: bytes,
            **kwargs: dict[Any, Any]
    ) -> bytes:
        return b'%b\r\n' % command

    def check_crc_login(self, login_packet: bytes) -> bool:
        body = login_packet[3:-6]
        crc = login_packet[-6:-2]
        return int(crc, 16) == crc16.arc(body)

    def check_crc_data(
            self,
            data_packet: bytes
    ) -> bool:
        return self.check_crc_login(login_packet=data_packet)

    def answer_login_packet(
            self,
            status: StatusAuth,
    ) -> bytes:
        return b'#AL#1\r\n'

    def answer_failed_login_packet(
            self,
            status: StatusAuth,
    ) -> Optional[bytes]:
        if status.error or status.authorization or status.crc:
            return b'#AL#0\r\n'
        elif status.password:
            return b'#AL#01\r\n'
        elif status.crc:
            return b'#AL#10\r\n'

    def answer_failed_packet(
            self,
            status: StatusAuth,
            meta: dict
    ) -> Optional[bytes]:
        pass

    def answer_packet(
            self,
            status: StatusParsing,
    ) -> Optional[bytes]:
        return b"#A%b#1\r\n" % self.metadata.last_type_packet

    def parsing_packet(
            self,
            bytes_data: bytes,
    ) -> Optional[list[PreMessage]]:
        _, packet_type, data = bytes_data.split(b'#')

        match packet_type:
            case b'D':
                packets = [self._parse_packet_d(data)]
            case b'SD':
                packets = [self._parse_packet_sd(data)]
            case b'B':
                packets = self._parse_packet_b(data)
            case _:
                packets = None

        self.metadata.last_type_packet = packet_type
        return packets

    def _parse_packet_sd(self, data: bytes) -> PreMessage:
        (date, _time,
         lat, lat_dir, lon, lon_dir,
         speed, course, alt, sats) = data.split(b';', 10)

        message = self._get_base_data((
            date, _time,
            lat, lat_dir, lon, lon_dir,
            speed, course, alt, sats
        ))
        return message

    def _parse_packet_d(self, data: bytes) -> PreMessage:
        (
            date, _time,
            lat, lat_dir, lon, lon_dir,
            speed, course, alt, sats, hdop,
            inputs, outputs, adc, ibutton, params, _
        ) = data.split(b';', 17)

        message = self._get_base_data(
            date, _time,
            lat, lat_dir, lon, lon_dir,
            speed, course, alt, sats
        )

        message.lbs.hdop = float(hdop) if hdop != self._EMPTY else None
        message.parameters.update({
            'ibutton': str(ibutton) if ibutton != self._EMPTY else None
        })

        if self._EMPTY != inputs and inputs:
            message.parameters.update({
                f"in_{num}": int(val)
                for num, val
                in enumerate(f"{int(inputs):b}"[::-1])
            })

        if self._EMPTY != outputs and outputs:
            message.parameters.update({
                f"out_{num}": int(val)
                for num, val
                in enumerate(f"{int(outputs):b}"[::-1])
            })

        if self._EMPTY != adc and adc:
            message.parameters.update({
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
            message.parameters.update({'parameters': list_parameters})
        return message

    def _parse_packet_b(self, data: bytes) -> list[PreMessage]:
        ready_packets = list()

        packets_b = data.split(b'|')
        for packet in packets_b:
            ready_packets.append(self._parse_packet_sd(packet))

        return ready_packets

    def _get_base_data(self, *args) -> PreMessage:
        (date, _time,
         lat, lat_dir, lon, lon_dir,
         speed, course, alt, sats) = args

        return PreMessage(**{
            'in_packet': self._get_time(date, _time),
            'latitude': self._get_lat(lat, lat_dir),
            'longitude': self._get_lon(lon, lon_dir),
            'speed': float(speed) if speed != self._EMPTY else None,
            'course': float(course) if course != self._EMPTY else None,
            'altitude': float(alt) if alt != self._EMPTY else None,
            'satellites': int(sats) if sats != self._EMPTY else None,
        })

    def _get_time(self, date: bytes, _time: bytes) -> int:
        if self._EMPTY not in (date, _time):
            return int(
                datetime(
                    year=int(date[4:6]) + 2000,
                    month=int(date[2:4]),
                    day=int(date[0:2]),
                    hour=int(_time[0:2]),
                    minute=int(_time[2:4]),
                    second=int(_time[4:6])
                ).timestamp()
            )
        return int(time())

    def _get_lat(self, lat: bytes, lat_dir: bytes) -> float:
        if self._EMPTY not in (lat, lat_dir):
            direction = 1 if lat_dir == b'N' else -1
            return (int(lat[:2]) + float(lat[2:]) / 60.) * direction

    def _get_lon(self, lon: bytes, lon_dir: bytes) -> float:
        if self._EMPTY not in (lon, lon_dir):
            direction = 1 if lon_dir == b'E' else -1
            return (int(lon[:3]) + float(lon[3:])) * direction
