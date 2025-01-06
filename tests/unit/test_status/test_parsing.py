import pytest
from src.status.parsing import StatusParsing
from src.protocol.abstract import AbstractProtocol


class MockProtocol(AbstractProtocol):
    def answer_packet(self, status, **kwargs):
        return b"packet_success"

    def answer_failed_data_packet(self, *args, status, **kwargs):
        return b"packet_failed"


def test_status_parsing_initialization_sets_correct_values():
    status = StatusParsing(crc=True, err=False)
    assert status.crc is True
    assert status.err is False


def test_correct_property_returns_true_when_crc_is_true_and_no_error():
    status = StatusParsing(crc=True, err=False)
    assert status.correct is True


def test_correct_property_returns_false_when_crc_is_false():
    status = StatusParsing(crc=False, err=False)
    assert status.correct is False


def test_correct_property_returns_false_when_error_is_true():
    status = StatusParsing(crc=True, err=True)
    assert status.correct is False


def test_make_answer_returns_packet_success_when_status_correct():
    status = StatusParsing(crc=True, err=False)
    handler = MockProtocol()
    assert status.make_answer(handler) == b"packet_success"


def test_make_answer_returns_packet_failed_when_status_not_correct():
    status = StatusParsing(crc=False, err=True)
    handler = MockProtocol()
    assert status.make_answer(handler) == b"packet_failed"
