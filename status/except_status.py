from typing import Optional

from ..status.abstract import Status


class StatusException(Status):

    __slots__ = '_err', '_err_type', '_err_args', '_err_str', '_err_func_name'

    def __init__(self):
        self._err: bool = False
        self._err_type: Optional[Exception] = None
        self._err_args: Optional[tuple] = None
        self._err_str: Optional[str] = None
        self._err_func_name: Optional[str] = None

    def __repr__(self):
        return repr(self)

    @property
    def correct(self) -> bool:
        return not self._err

    @property
    def error(self) -> bool:
        return self._err

    @error.setter
    def error(self, value):
        self._err = value

    @property
    def type(self) -> Optional[Exception]:
        return self._err_type

    @type.setter
    def type(self, value):
        self._err_type = value

    @property
    def args(self) -> Optional[tuple]:
        return self._err_args

    @args.setter
    def args(self, value):
        self._err_args = value

    @property
    def description(self) -> Optional[str]:
        return self._err_str

    @description.setter
    def description(self, value):
        self._err_str = value

    @property
    def location(self) -> Optional[str]:
        return self._err_func_name

    @location.setter
    def location(self, value):
        self._err_func_name = value


def exception_unit_wrapper(func):

    def exception_analyze(
            *args,
            **kwargs
    ) -> tuple[StatusException, Optional[list[dict]]]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Parsing exception {e}")
            status = StatusException()
            status.error = True
            status.type = type(e)
            status.description = e
            status.location = func.__name__

            return status, None

    return exception_analyze
