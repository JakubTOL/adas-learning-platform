import logging

from zalp.application.concurrency import Service
from zalp.domain.psu import KoradIncorrectResponseException

logger = logging.getLogger(__name__)


class UpdateOutputService(Service):
    def __init__(self, period, psu, callback):
        super().__init__(period)
        self.psu = psu
        self.callback = callback

    def run(self):
        try:
            output = self.psu.get_output()
            self.callback(output)
        except KoradIncorrectResponseException:
            logger.exception('UpdateOutputService: Error during Korad communication')
