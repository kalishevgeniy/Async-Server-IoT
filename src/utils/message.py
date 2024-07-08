from typing import Any, Optional

from pydantic import BaseModel
from datetime import datetime, timezone


class Time(BaseModel):
    receive: datetime = datetime.now(tz=timezone.utc)
    in_packet: datetime


class Navigation(BaseModel):
    latitude: float
    longitude: float
    altitude: float
    course: int
    satellites: int


class LBS(BaseModel):
    hdop: float
    mcc: int
    mnc: int
    lac: int
    cid: int


class Message(BaseModel):
    imei: str
    time_: Time
    navigation: Navigation
    speed: Optional[int]
    lbs: Optional[LBS]
    parameters: Optional[dict[Any, Any]]
