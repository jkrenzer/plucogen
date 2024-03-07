import logging
from enum import Enum
from functools import update_wrapper
from inspect import signature
from logging import (
    Logger,
    RootLogger,
    StreamHandler,
    basicConfig,
    getLogger,
    handlers,
    root,
    shutdown,
)
from typing import TYPE_CHECKING

logging.captureWarnings(True)
logging.basicConfig()


class LogLevels(int, Enum):
    notset = logging.NOTSET
    debug = logging.DEBUG
    info = logging.INFO
    warn = logging.WARN
    error = logging.ERROR
    critical = logging.CRITICAL


default_handler = root.handlers.pop()
startup_handler = handlers.MemoryHandler(capacity=1000, flushLevel=1000)
_start_up = True
root.setLevel(logging.NOTSET)
root.addHandler(startup_handler)


def start(level: int = logging.NOTSET):
    global _start_up
    default_handler.setLevel(level)
    startup_handler.buffer = list(
        filter(lambda r: r.levelno >= level, startup_handler.buffer)
    )
    startup_handler.setTarget(default_handler)
    startup_handler.flush()
    root.removeHandler(startup_handler)
    root.addHandler(default_handler)
    _start_up = False


def _basicConfig(level: int, **kwargs) -> None:
    global _start_up

    if _start_up:
        start(level)
    signature(logging.basicConfig).bind(level=level, **kwargs)
    return logging.basicConfig(level=level, **kwargs)


basicConfig = update_wrapper(wrapper=_basicConfig, wrapped=logging.basicConfig)
