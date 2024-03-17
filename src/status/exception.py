from typing import Optional

from .abstract import Status
from src.utils.logger import Logger
from ..protocol.abstract import AbstractProtocol


class StatusException(Status):

    __slots__ = 'err', 'err_type', 'err_args', 'err_str', 'err_func_name'

    def __init__(self):
        self.err: bool = False
        self.err_type: Optional[Exception] = None
        self.err_args: Optional[tuple] = None
        self.err_str: Optional[str] = None
        self.err_func_name: Optional[str] = None

    def __repr__(self):
        return repr(self)

    @property
    def correct(self) -> bool:
        return not self.err

    def make_answer(
            self,
            metadata: dict,
            handler: AbstractProtocol
    ) -> bytes:
        return handler.answer_exception(
            status=self,
            metadata=metadata
        )


def exception_unit_wrapper(func):
    def exception_analyze(
            *args,
            **kwargs
    ) -> tuple[StatusException, Optional[list[dict]]]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            Logger().warning(
                f"Parsing exception {e} {args} {kwargs} {func.__name__}"
            )
            status = StatusException()
            status.error = True
            status.type = type(e)
            status.description = e
            status.location = func.__name__

            return status, None

    return exception_analyze
