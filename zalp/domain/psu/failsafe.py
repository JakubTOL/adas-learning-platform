import functools
import logging

from zalp.domain.psu.exceptions import KoradIncorrectResponseException

CONSECUTIVE_FAILURES_FOR_REINIT = 3

logger = logging.getLogger(__name__)


def failsafe(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._failsafe_enabled and \
                self._consecutive_failures >= CONSECUTIVE_FAILURES_FOR_REINIT:
            logger.warning('Korad: Too many consecutive failures, triggering re-init')

            # disable failsafe mechanism during re-init try
            self._failsafe_enabled = False

            try:
                self.connect()
            except Exception:
                # increment failure count
                self._consecutive_failures += 1
                raise
            finally:
                # let application try to re-init later
                self._failsafe_enabled = True
        try:
            ret = func(self, *args, **kwargs)
            # no failure
            self._consecutive_failures = 0
            return ret
        except KoradIncorrectResponseException:
            # increment failure count
            self._consecutive_failures += 1

            # re-raise exception, error still happened
            # let application try again in next scheduled thread
            raise

    return wrapper
