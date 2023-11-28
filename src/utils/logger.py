import os
import sys

from loguru import logger


class Logger:

    _logger: logger = None

    def __new__(cls, *args, **kwargs) -> logger:
        if cls._logger is None:
            cls._logger = cls._init_loger()
        return cls._logger

    @classmethod
    def _init_loger(cls):
        logger.remove(0)
        logger.add(sys.stdout, level=cls._get_log_lvl())
        return logger

    @staticmethod
    def _get_log_lvl():
        return os.getenv('LOG_LEVEL', 'DEBUG')
