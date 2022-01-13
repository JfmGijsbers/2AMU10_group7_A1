# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 14:29:49 2022

@author: yihez
"""
# timer.py
import functools
import time
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, Optional

from contextlib import ContextDecorator


# let Timer class inherit ContextDecorator

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer(ContextDecorator):
    """
    Can be used as:
        * Class
        t = Timer(name="class")
        t.start()
        # Do something
        t.stop()
        * Context manager
        with Timer(name="context manager"):
            # Do something
        * decorator
        @Timer(name="Decorator")
        def stuff():
            # Do Something

    """
    timers: ClassVar[Dict[str, float]] = dict()
    name: Optional[str] = None
    text: str = "Elapsed time: {:0.4f} seconds"
    logger: Optional[Callable[[str], None]] = print
    _start_time: Optional[float] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Initialization: add timer to dict of timers"""
        if self.name is not None:
            self.timers.setdefault(self.name, 0)

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError("Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError("Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        if self.logger:
            self.logger(self.text.format(elapsed_time))
        if self.name:
            self.timers[self.name] += elapsed_time
        return elapsed_time

    def __enter__(self):
        """Start a new timer as a context manager"""
        self.start()
        return self

    def __exit__(self, *exc_info):
        """Stop the context manager timer"""
        self.stop()

    # if ContextDecorator is disabled
    # def __call__(self, func):
    #     """Support using Timer as decorator"""
    #     @functools.wraps(func)
    #     def wrapper_timer(*args, **kwargs):
    #         with self:
    #             return func(*args, **kwargs)
    #     return wrapper_timer
