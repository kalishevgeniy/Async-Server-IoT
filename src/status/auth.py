from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from .abstract import Status


if TYPE_CHECKING:
    from ..protocol.abstract import AbstractProtocol


class StatusAuth(Status):
    __slots__ = "crc", "authorization", "password", "error"

    def __init__(self):
        self.crc: Optional[bool] = None
        self.authorization: Optional[bool] = None
        self.password: Optional[bool] = None
        self.error = None

    def __repr__(self):
        return f"Status authorization: {self.correct}"

    @property
    def correct(self) -> bool:
        return all((
            self.crc, self.authorization, self.password, not self.error
        ))

    def make_answer(
            self,
            handler: AbstractProtocol
    ) -> bytes:
        if self.correct:
            return handler.answer_login_packet(status=self)
        else:
            return handler.answer_failed_login_packet(status=self)
