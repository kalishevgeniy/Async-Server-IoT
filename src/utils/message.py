from typing import Any, Optional

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class Time(BaseModel):
    receive: datetime = datetime.now(tz=timezone.utc)
    in_packet: datetime = datetime.now(tz=timezone.utc)


class Navigation(BaseModel):
    latitude: float = Field(ge=-90, le=90, default=0)
    longitude: float = Field(ge=-180, le=-180, default=0)
    altitude: float = Field(ge=-0xFFFF, le=0xFFFF, default=0)
    course: int = Field(ge=0, le=360, default=0)
    satellites: int = Field(ge=0, le=0xFF, default=0)
    speed: Optional[int] = Field(ge=0, default=0)


class LBS(BaseModel):
    hdop: Optional[float] = Field(default=0.0)
    mcc: Optional[int] = Field(default=0)
    mnc: Optional[int] = Field(default=0)
    lac: Optional[int] = Field(default=0)
    cid: Optional[int] = Field(default=0)


class PreMessage(BaseModel):
    time_: Optional[Time] = Time()
    navigation: Optional[Navigation] = Navigation()
    lbs: Optional[LBS]
    parameters: Optional[dict[Any, Any]] = Field(default=dict())


class Message(PreMessage):
    imei: str
