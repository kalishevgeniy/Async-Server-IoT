from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from ..protocol.abstract import AbstractProtocol

from typing import Protocol


class Status(Protocol):

    def correct(self) -> bool:
        """Check correct all field"""

    def make_answer(
            self,
            handler: AbstractProtocol
    ) -> bytes:
        """Return specific answer for handler"""
