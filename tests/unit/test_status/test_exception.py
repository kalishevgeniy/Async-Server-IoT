import pytest
from src.status.exception import StatusException, exception_wrapper
from src.protocol.abstract import AbstractProtocol


class MockProtocol(AbstractProtocol):
    def answer_exception(self, status, **kwargs):
        return b"exception_handled"


def test_status_exception_initialization_sets_correct_values():
    err = ValueError('test_status')
    status = StatusException(
        err=True,
        err_type=err,
        err_args=("error",),
        err_str="error",
        err_func_name="func"
    )
    assert status._err is True
    assert status.err_type == err
    assert status.err_args == ("error",)
    assert status.err_str == "error"
    assert status.err_func_name == "func"


def test_correct_property_returns_false_when_error_present():
    status = StatusException(
        err=True,
        err_type=ValueError('test_status'),
        err_args=("error",),
        err_str="error",
        err_func_name="func"
    )
    assert status.correct is False


def test_correct_property_returns_true_when_no_error():
    status = StatusException(
        err=False,
        err_type=None,
        err_args=(),
        err_str="",
        err_func_name="func"
    )
    assert status.correct is True


def test_make_answer_returns_exception_handled():
    status = StatusException(
        err=True,
        err_type=ValueError('test_make_answer'),
        err_args=("error",),
        err_str="error",
        err_func_name="func"
    )
    handler = MockProtocol()
    assert status.make_answer(handler) == b"exception_handled"


def test_exception_wrapper_catches_exception_and_returns_status_exception():
    err = ValueError('test_exception_wrapper')

    @exception_wrapper
    def func_that_raises():
        raise err

    status, result, response = func_that_raises()
    assert isinstance(status, StatusException)
    assert status.err_type == err
    assert status.err_str == "test_exception_wrapper"
    assert result is None
    assert response == b''
