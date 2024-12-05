from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class PacketTypeEnum(str, Enum):
    MESSAGE = "message"
    COMMAND_ANSWER = "command_answer"


class Navigation(BaseModel):
    latitude: float = Field(ge=-90.0, le=90.0, default=0)
    longitude: float = Field(ge=-180.0, le=180.0, default=0)
    altitude: float = Field(ge=-0xFFFF, le=0xFFFF, default=0)
    course: int = Field(ge=0, le=360, default=0)
    satellites: int = Field(ge=0, le=0xFF, default=0)
    speed: int = Field(ge=0, default=0)


class LBS(BaseModel):
    hdop: Optional[float] = Field(default=None)
    pdop: Optional[float] = Field(default=None)
    mcc: Optional[int] = Field(default=None)
    mnc: Optional[int] = Field(default=None)
    lac: Optional[int] = Field(default=None)
    cid: Optional[int] = Field(default=None)


class Message(BaseModel):
    time_: datetime = datetime.now(tz=timezone.utc)
    navigation: Navigation
    lbs: Optional[LBS] = None
    parameters: Optional[dict[Any, Any]] = Field(default=dict())

    packet_type: PacketTypeEnum = PacketTypeEnum.MESSAGE


class LoginMessage(BaseModel):
    imei: str
    password: Optional[str] = Field(default=None)
    messages: Optional[list[Message]] = Field(default=None)
