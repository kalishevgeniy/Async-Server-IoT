from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Any

from .abstract import Status

if TYPE_CHECKING:
    from ..protocol.abstract import AbstractProtocol


class StatusAuth(Status):
    __slots__ = "_crc", "_authorization", "_password", "_error"

    def __init__(
            self,
            crc: bool = True,
            authorization: bool = True,
            password: bool = True,
            error: bool = False,
            description: Optional[str] = None,
    ):
        self.crc: bool = crc
        self.authorization: bool = authorization
        self.password: bool = password
        self.error = error

        self._description = description

    def __repr__(self):
        return (
            f"<StatusAuth: "
            f"{self.crc=} "
            f"{self.authorization=} "
            f"{self.password=} "
            f"{self.error=} "
            f"{self._description=}>"
        )

    @property
    def correct(self) -> bool:
        return all((
            self.crc,
            self.authorization,
            self.password,
            not self.error
        ))

    def make_answer(
            self,
            handler: AbstractProtocol,
            *args: Any,
            **kwargs: Any
    ) -> Optional[bytes]:
        if self.correct:
            return handler.answer_login_packet(status=self, **kwargs)
        else:
            return handler.answer_failed_login_packet(status=self, **kwargs)
