from datetime import datetime
from typing import Optional

from src.utils.meta import MetaData


class Unit:
    def __init__(self):
        self.metadata = MetaData()

        self._is_authorized = False
        self._id = None
        self._imei = None
        self._password = None
        self._connected_at = datetime.now()
        self.disconnected_at = None

    def __repr__(self):
        return (
            f"<Unit "
            f"id={self._id}, "
            f"imei={self._imei}, "
            f"connected_at={self._connected_at}, "
            f"disconnected_at={self.disconnected_at}"
            f">"
        )

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password

    @property
    def is_authorized(self) -> bool:
        return self._is_authorized

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, id_: int) -> None:
        self._id = id_
        self._is_authorized = True

    @property
    def imei(self) -> Optional[str]:
        return self._imei

    @imei.setter
    def imei(self, imei: str) -> None:
        if imei != self._imei:
            self._is_authorized = False
            self._id = None

        self._imei = imei
