from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from .abstract import Status

if TYPE_CHECKING:
    from ..protocol.abstract import AbstractProtocol


class StatusParsing(Status):
    __slots__ = "err", "crc"

    def __init__(
            self,
            crc: bool = False,
            err: bool = False,
    ):
        self.err = err
        self.crc = crc

    def __repr__(self):
        return (
            f"StatusParsing("
            f"err={self.err}, "
            f"crc={self.crc}"
            f")"
        )

    @property
    def correct(self) -> bool:
        return all((
            not self.err, self.crc
        ))

    def make_answer(
            self,
            handler: AbstractProtocol,
            *args,
            **kwargs
    ) -> Optional[bytes]:
        if self.correct:
            return handler.answer_packet(
                status=self,
                **kwargs
            )
        else:
            return handler.answer_failed_data_packet(
                *args,
                status=self,
                **kwargs
            )
