import logging

from zalp.application.concurrency import Service
from zalp.domain.psu import KoradIncorrectResponseException

logger = logging.getLogger(__name__)


class GetVoltageService(Service):
    def __init__(self, period, psu, callback):
        super().__init__(period)
        self.psu = psu
        self.callback = callback

    def run(self):
        try:
            voltage = self.psu.get_voltage()
            self.callback(voltage)
        except KoradIncorrectResponseException:
            logger.exception('GetVoltageService: Error during Korad communication')
