import os
import time
from typing import Optional

from zalp.application.concurrency import run_in_thread
from zalp.application.psu.get_current import GetCurrentService
from zalp.application.psu.get_voltage import GetVoltageService
from zalp.application.psu.update_output import UpdateOutputService
from zalp.domain.psu import Korad
from zalp.infrastructure.serial import KoradSerialInterface


class PsuService:
    def __init__(self):
        self.get_voltage_service = None
        self.get_current_service = None
        self.update_output_service = None

        self.interface = KoradSerialInterface(
            port=os.getenv('PSU_SERIAL_PORT'),
            baudrate=int(os.getenv('PSU_SERIAL_BAUDRATE'))
        )
        self.psu = Korad(
            interface=self.interface
            # interface=MockKoradSerialInterface()
        )
        self.psu.connect()

    def start(self,
              get_voltage_callback=None,
              get_current_callback=None,
              update_output_callback=None):
        self.get_voltage_service = GetVoltageService(
            period=1,
            psu=self.psu,
            callback=get_voltage_callback
        )
        self.get_current_service = GetCurrentService(
            period=1,
            psu=self.psu,
            callback=get_current_callback
        )
        self.update_output_service = UpdateOutputService(
            period=1,
            psu=self.psu,
            callback=update_output_callback
        )
        self.get_voltage_service.start()
        self.get_current_service.start()
        self.update_output_service.start()

    # TODO: refactor. Stopped service should never be used again if it stores a callback reference.
    #       Either all references should be passed during "start" call or service should be destroyed
    #       immediately when stopped, like below, which is probably less clean.
    def stop(self):
        self.set_output(False)
        time.sleep(0.2)
        if self.get_voltage_service:
            self.get_voltage_service.stop()
        if self.get_current_service:
            self.get_current_service.stop()
        if self.update_output_service:
            self.update_output_service.stop()

        self.get_voltage_service = None
        self.get_current_service = None
        self.update_output_service = None

    # TODO: remove. Behavior moved to services
    # def get_voltage(self, callback):
    #     voltage = self.psu.get_voltage()
    #     callback(voltage)
    #
    # def update_output(self, callback):
    #     output = self.psu.get_output()
    #     callback(output)

    def set_default(self):
        self.set_voltage()
        self.set_output(True)

    @run_in_thread
    def set_voltage(self, voltage: Optional[float] = None):
        self.psu.set_voltage(voltage)

    @run_in_thread
    def set_output(self, on: bool = True):
        self.psu.set_output(on)
        # force update if service is available
        # Commented out - possible bug here
        # if self.update_output_service:
        #     self.update_output_service.run()
