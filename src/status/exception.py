from __future__ import annotations

from functools import wraps
from typing import Optional, TYPE_CHECKING, Any

from traceback import format_exc as tb

from .abstract import Status
import logging

if TYPE_CHECKING:
    from ..protocol.abstract import AbstractProtocol


class StatusException(Status):
    __slots__ = 'err', 'err_type', 'err_args', 'err_str', 'err_func_name'

    def __init__(
            self,
            err: bool,
            err_args: Optional[tuple],
            err_str: Optional[str],
            err_func_name: Optional[str],
            err_type: Optional[Exception],
    ):
        self._err = err
        self.err_type = err_type
        self.err_args = err_args
        self.err_str = err_str
        self.err_func_name = err_func_name

    def __repr__(self):
        return f"<StatusException {self.err_type}>"

    @property
    def correct(self) -> bool:
        return not self._err

    def make_answer(
            self,
            handler: AbstractProtocol,
            *args,
            **kwargs
    ) -> Optional[bytes]:
        return handler.answer_exception(status=self, **kwargs)


def exception_wrapper(func):

    @wraps(func)
    def wrapper(
            *args,
            **kwargs
    ) -> tuple[StatusException, Optional[Any], bytes]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(
                f"Parsing exception {e} \n"
                f"arguments {(args, kwargs)} \n"
            )
            logging.debug(tb())

            status = StatusException(
                err=True,
                err_type=e,
                err_args=e.args,
                err_str=str(e),
                err_func_name=func.__name__
            )

            return status, None, b''

    return wrapper
