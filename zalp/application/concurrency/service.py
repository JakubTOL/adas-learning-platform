import logging
import time
from abc import ABC, abstractmethod
from threading import Thread, Event

logger = logging.getLogger(__name__)


class Service(ABC):
    """
    Abstract class implementing the behaviour of a periodic service.
    Service can be started, which then periodically calls the method `run`.

    Code implemented in the method `run` will be executed in the newly created thread.
    Blocking in this method for longer than defined period will be logged as warning.
    """

    def __init__(self, period):
        self.period = period

        self.cancel_event = Event()
        self.thread = None

    def start(self):
        self.cancel_event.clear()
        self.thread = Thread(target=self._run_internal)
        self.thread.start()

    def stop(self):
        self.cancel_event.set()

    def _run_internal(self):
        cancelled = False
        while True:
            start_time = time.time()
            self.run()
            stop_time = time.time()
            run_duration = stop_time - start_time
            if run_duration > self.period:
                logger.warning(f'Service: Service {self.__class__.__name__} did not sleep, '
                               f'blocked for longer than defined period ({self.period} s)')
            else:
                cancelled = self.cancel_event.wait(self.period)
            if cancelled:
                break
        self.thread = None

    @abstractmethod
    def run(self):
        """
        Main method of the service, run every period in its own thread.
        Override in concrete implementations.
        Use `self.parent` to access methods of parent class to perform the tasks.
        """
        pass
