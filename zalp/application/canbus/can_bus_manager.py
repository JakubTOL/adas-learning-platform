import logging
import os

from zalp.application.concurrency import run_in_thread
from zalp.domain.canbus import CanBus, DiagnosticSubFunction
from zalp.infrastructure.canbus import CanInterface
from .diagnostic import EXTENDED_SESSION_SUBFUNCTION, CLEAR_ALL_DTCS_SUBFUNCTION, \
    DEFAULT_SESSION_SUBFUNCTION

logger = logging.getLogger(__name__)


class CanBusManager:
    def __init__(self,
                 name,
                 dbc_path,
                 on_message,
                 did_list=None
                 ):
        self.interface = CanInterface(name=name)
        self.bus = CanBus(
            name=name,
            interface=self.interface,
            dbc_path=dbc_path,
            dut_name=os.getenv('CAN_DUT_NAME'),
            on_message=on_message,
            did_list=did_list)

        self.diagnostic_tx_callbacks = []
        self.diagnostic_rx_callbacks = []

    def set_signal_value(self, msg_name, signal_name, value):
        self.bus.set_signal_value(msg_name, signal_name, value)

    def get_signal_value(self, msg_name, signal_name):
        return self.bus.get_signal_value(msg_name, signal_name)

    def start_rx_handler(self):
        self.bus.start_rx_handler()

    def stop_rx_handler(self):
        self.bus.stop_rx_handler()

    def start_restbus(self):
        self.bus.start_restbus()

    def stop_restbus(self):
        self.bus.stop_restbus()

    def shutdown(self):
        self.interface.shutdown()

    def send_diagnostic_request(self, subfunction: DiagnosticSubFunction):
        if self.bus.uds_client is None:
            return

        for callback in self.diagnostic_tx_callbacks:
            callback(subfunction)
        response = self.bus.uds_client.send_diagnostic_request(subfunction)
        for callback in self.diagnostic_rx_callbacks:
            callback(response)

        return response

    @run_in_thread
    def clear_all_dtcs(self):
        """
        Convenience function to clear all DTCs.
        """
        tester_present = self.get_tester_present()
        self.send_diagnostic_request(EXTENDED_SESSION_SUBFUNCTION)  # Will enable TesterPresent
        self.send_diagnostic_request(CLEAR_ALL_DTCS_SUBFUNCTION)
        self.send_diagnostic_request(DEFAULT_SESSION_SUBFUNCTION)

        # Disable TesterPresent if was not enabled before the start of this procedure
        if not tester_present:
            self.set_tester_present(False)

    def add_diagnostic_tx_callback(self, callback):
        self.diagnostic_tx_callbacks.append(callback)

    def remove_diagnostic_tx_callback(self, callback):
        self.diagnostic_tx_callbacks.remove(callback)

    def add_diagnostic_rx_callback(self, callback):
        self.diagnostic_rx_callbacks.append(callback)

    def remove_diagnostic_rx_callback(self, callback):
        self.diagnostic_rx_callbacks.remove(callback)

    def get_tester_present(self):
        if self.bus.uds_client is None:
            return False
        return self.bus.uds_client.get_tester_present()

    def set_tester_present(self, on: bool):
        if self.bus.uds_client is None:
            return
        return self.bus.uds_client.set_tester_present(on)
