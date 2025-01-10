from enum import Enum
from typing import Optional, Union, Any

from datetime import datetime, timezone


Time = Union[int, float, datetime]


class PacketTypeEnum(str, Enum):
    MESSAGE = "message"
    COMMAND_ANSWER = "command_answer"


class Navigation:
    def __init__(
        self,
        latitude: float,
        longitude: float,
        altitude: float,
        course: int,
        satellites: int,
        speed: int,
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.course = course
        self.satellites = satellites
        self.speed = speed

    def __repr__(self):
        return (
            f"<Navigation "
            f"latitude={self.latitude} "
            f"longitude={self.longitude}>"
        )

    @property
    def latitude(self) -> float:
        return self._latitude

    @latitude.setter
    def latitude(self, latitude: float):
        if not isinstance(latitude, float):
            raise TypeError("latitude must be a float")

        if not (-90.0 <= latitude <= 90.0):
            latitude = 0

        self._latitude = round(latitude, 6)

    @property
    def longitude(self) -> float:
        return self._longitude

    @longitude.setter
    def longitude(self, longitude: float):
        if not isinstance(longitude, float):
            raise TypeError("longitude must be a float")

        if not (-180.0 <= longitude <= 180.0):
            longitude = 0

        self._longitude = round(longitude, 6)

    @property
    def altitude(self) -> float:
        return self._altitude

    @altitude.setter
    def altitude(self, altitude: float):
        if not isinstance(altitude, float):
            raise TypeError("altitude must be a float")

        if not (-0xFFFF <= altitude <= 0xFFFF):
            altitude = 0

        self._altitude = altitude

    @property
    def course(self) -> int:
        return self._course

    @course.setter
    def course(self, course: Union[int, float]):
        if not isinstance(course, (int, float)):
            raise TypeError("course must be a int")

        if not (0 <= course <= 360):
            course = 0

        self._course = int(course)

    @property
    def satellites(self) -> int:
        return self._satellites

    @satellites.setter
    def satellites(self, satellites: int):
        if not isinstance(satellites, int):
            raise TypeError("satellites must be a int")

        if not (0 <= satellites <= 0xFF):
            satellites = 0

        self._satellites = satellites

    @property
    def speed(self) -> int:
        return self._speed

    @speed.setter
    def speed(self, speed: int):
        if not isinstance(speed, int):
            raise TypeError("speed must be a int")

        if not (0 <= speed <= 0x7FFF):
            speed = 0

        self._speed = speed


class LBS:
    def __init__(
            self,
            hdop: Optional[float] = None,
            pdop: Optional[float] = None,
            mcc: Optional[int] = None,
            mnc: Optional[int] = None,
            lac: Optional[int] = None,
            cid: Optional[int] = None,
    ):
        self.hdop = hdop
        self.pdop = pdop
        self.mcc = mcc
        self.mnc = mnc
        self.lac = lac
        self.cid = cid

    @property
    def hdop(self) -> Optional[float]:
        return self._hdop

    @hdop.setter
    def hdop(self, value: Union[float, int, str]):
        self._hdop: Optional[float]
        try:
            self._hdop = float(value)
        except ValueError:
            self._hdop = None

    @property
    def pdop(self) -> Optional[float]:
        return self._pdop

    @pdop.setter
    def pdop(self, value: Union[float, int, str]):
        self._pdop: Optional[float]
        try:
            self._pdop = float(value)
        except ValueError:
            self._pdop = None

    @property
    def mcc(self) -> Optional[int]:
        return self._mcc

    @mcc.setter
    def mcc(self, value: int):
        self._mcc = value

    @property
    def mnc(self) -> Optional[int]:
        return self._mnc

    @mnc.setter
    def mnc(self, value: int):
        self._mnc = value

    @property
    def lac(self) -> Optional[int]:
        return self._lac

    @lac.setter
    def lac(self, value: int):
        self._lac = value

    @property
    def cid(self) -> Optional[int]:
        return self._cid

    @cid.setter
    def cid(self, value: int):
        self._cid = value


class Parameters:
    def __init__(
            self,
            **kwargs: Optional[dict[str, str]]
    ):
        if kwargs:
            self._parameters = kwargs
        else:
            self._parameters = dict()

    def __repr__(self):
        return str(self._parameters)

    def get(self) -> dict[str, str]:
        return self._parameters

    def update(self, kwargs: dict[Any, Any]):
        self._parameters.update(**kwargs)


class Message:
    def __init__(
            self,
            time_: Time,
            navigation: Navigation,
            lbs: Optional[LBS] = None,
            parameters: Optional[dict[str, str]] = None,
            packet_type: PacketTypeEnum = PacketTypeEnum.MESSAGE,
    ):
        self.time_ = time_
        self.navigation = navigation
        self.lbs = lbs
        self.parameters = Parameters(**parameters if parameters else dict())
        self.packet_type = packet_type

    def __repr__(self) -> str:
        return (
            f"Message("
            f"time={self.time_},"
            f"navigation={self.navigation}),"
            f"lbs={self.lbs},"
            f"parameters={self.parameters},"
            f"packet_type={self.packet_type}"
        )

    @property
    def time_(self) -> Time:
        return self._time

    @time_.setter
    def time_(self, time_: Time):
        if isinstance(time_, (int, float)):
            self._time = datetime.fromtimestamp(time_)
        elif isinstance(time_, datetime):
            self._time = time_.replace(tzinfo=timezone.utc)
        else:
            raise TypeError(f"Invalid type {type(time_)}")

    @property
    def packet_type(self) -> str:
        return self._packet_type

    @packet_type.setter
    def packet_type(self, packet_type: PacketTypeEnum):
        self._packet_type = packet_type


class LoginMessage:
    __slots__ = ("_imei", "_password", "_messages")

    def __init__(
            self,
            imei: str,
            password: Optional[str] = None,
            messages: Optional[list[Message]] = None,
    ):
        self.imei = imei
        self.password = password
        self.messages = messages

    def __repr__(self):
        return (
            f"LoginMessage("
            f"imei={self.imei},"
            f"password={self.password},"
            f"messages=count("
            f"{len(self.messages) if self.messages is not None else 0}"
            f")"
            f""
        )

    @property
    def imei(self):
        return self._imei

    @imei.setter
    def imei(self, imei: str):
        self._imei = imei

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password: Optional[str]):
        self._password = password

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, messages: Optional[list[Message]]):
        self._messages = messages
