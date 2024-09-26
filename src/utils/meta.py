from typing import Any, Optional

from pydantic import BaseModel, Field
from datetime import datetime, timezone


class MetaData:

    def __init__(self):
        self._imei: Optional[str] = None

    @property
    def imei(self) -> str:
        return self._imei

    @imei.getter
    def imei(self) -> Optional[str]:
        return self._imei

    @imei.setter
    def imei(self, imei: str) -> None:
        self._imei = imei
