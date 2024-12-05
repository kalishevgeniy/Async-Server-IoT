from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from ..protocol.abstract import AbstractProtocol

from typing import Protocol


class Status(Protocol):

    @property
    def correct(self) -> bool:
        """Check correct all field"""

    def make_answer(
            self,
            handler: AbstractProtocol,
            *args: Any,
            **kwargs: Any
    ) -> Optional[bytes]:
        """Return specific answer for handler"""
