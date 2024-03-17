from typing import Any, Optional

from pydantic import BaseModel
from datetime import datetime, timezone


class TimeP(BaseModel):
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
    time_object: TimeP
    navigation: Navigation
    speed: int
    lbs: Optional[LBS]
    parameters: dict[str, Any]
