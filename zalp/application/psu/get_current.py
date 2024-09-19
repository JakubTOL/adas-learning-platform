import logging

from zalp.application.concurrency import Service
from zalp.domain.psu import KoradIncorrectResponseException

logger = logging.getLogger(__name__)


class GetCurrentService(Service):
    def __init__(self, period, psu, callback):
        super().__init__(period)
        self.psu = psu
        self.callback = callback

    def run(self):
        try:
            current = self.psu.get_current()
            self.callback(current)
        except KoradIncorrectResponseException:
            logger.exception('GetCurrentService: Error during Korad communication')
