import time
from dataclasses import dataclass, field
from typing import Callable, ClassVar, Dict, Optional

from contextlib import ContextDecorator


class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


@dataclass
class Timer(ContextDecorator):
    """
    This timer class is based on the following tutorial:
        https://realpython.com/python-timer/
    This timer class can be used to time pieces of the code in three different ways:
    1. As a Class
        t = Timer(name="class")
        t.start()
        # Do something
        t.stop()
    2. As a Context manager
        with Timer(name="context manager"):
            # Do something
    3. As a decorator
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
