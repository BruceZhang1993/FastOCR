from typing import Dict

from fastocr.consts import APP_CACHE_DIR
from fastocr.util import Singleton
import logging
import logging.config

DEFAULT_NAME = 'default'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'file_formatter': {
            'format': '[%(levelname)8s] %(asctime)s %(message)s | %(filename)s:%(lineno)d'
        },
        'simple_formatter': {
            'format': '[%(levelname)8s] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple_formatter',
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'file_formatter',
            'level': 'DEBUG',
            'filename': (APP_CACHE_DIR / 'runtime_log.log').as_posix(),
            'maxBytes': 102400,
            'backupCount': 5
        }
    },
    'loggers': {
        'default': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
}


class AppLogger(metaclass=Singleton):
    """
    AppLogger a simple wrapper for logging
    """
    def __init__(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        self.loggers: Dict[str, logging.Logger] = {}

    def get_logger(self, name=DEFAULT_NAME) -> logging.Logger:
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(name)
        return self.loggers[name]

    def critical(self, msg, *args, logger_name=DEFAULT_NAME, **kwargs):
        self.get_logger(logger_name).critical(msg, *args, **kwargs)

    def exception(self, msg, *args, logger_name=DEFAULT_NAME, exc_info=True, **kwargs):
        self.get_logger(logger_name).exception(msg, *args, exc_info=exc_info, **kwargs)

    def log(self, level, msg, *args, logger_name=DEFAULT_NAME, **kwargs):
        self.get_logger(logger_name).log(level, msg, *args, **kwargs)

    def error(self, msg, *args, logger_name=DEFAULT_NAME, **kwargs):
        self.get_logger(logger_name).error(msg, *args, **kwargs)

    def warning(self, msg, *args, logger_name=DEFAULT_NAME, **kwargs):
        self.get_logger(logger_name).warning(msg, *args, **kwargs)

    def info(self, msg, *args, logger_name=DEFAULT_NAME, **kwargs):
        self.get_logger(logger_name).info(msg, *args, **kwargs)

    def debug(self, msg, *args, logger_name=DEFAULT_NAME, **kwargs):
        self.get_logger(logger_name).debug(msg, *args, **kwargs)

    warn = warning
    fatal = critical
