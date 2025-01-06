import pytest
from src.status.auth import StatusAuth
from src.protocol.abstract import AbstractProtocol


class MockProtocol(AbstractProtocol):
    def answer_login_packet(self, status, **kwargs):
        return b"login_success"

    def answer_failed_login_packet(self, status, **kwargs):
        return b"login_failed"


def test_status_auth_initialization_sets_correct_values():
    status = StatusAuth(
        crc=True,
        authorization=True,
        password=True,
        error=False,
        description="All good"
    )
    assert status.crc is True
    assert status.authorization is True
    assert status.password is True
    assert status.error is False
    assert status._description == "All good"


def test_correct_property_returns_true_when_all_conditions_met():
    status = StatusAuth(
        crc=True,
        authorization=True,
        password=True,
        error=False
    )
    assert status.correct is True


def test_correct_property_returns_false_when_any_condition_not_met():
    status = StatusAuth(
        crc=False,
        authorization=True,
        password=True,
        error=False
    )
    assert status.correct is False


def test_make_answer_returns_login_success_when_status_correct():
    status = StatusAuth(
        crc=True,
        authorization=True,
        password=True,
        error=False
    )
    handler = MockProtocol()
    assert status.make_answer(handler) == b"login_success"


def test_make_answer_returns_login_failed_when_status_not_correct():
    status = StatusAuth(
        crc=True, 
        authorization=False,
        password=True,
        error=False
    )
    handler = MockProtocol()
    assert status.make_answer(handler) == b"login_failed"
