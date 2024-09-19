import logging

import bitstruct
import cantools

from .diagnostic import UdsClient
from .parse_dbc import parse_dbc
from .rx_handler import RxHandler
from .util import is_not_sent_by

logger = logging.getLogger(__name__)


class CanBus:
    def __init__(self,
                 name,
                 interface,
                 dbc_path,
                 dut_name,
                 on_message,
                 did_list
                 ):
        self.name = name
        self.interface = interface
        self.dbc = parse_dbc(dbc_path)
        self.dut_name = dut_name
        self.did_list = did_list

        """
        TODO:
        Does not implement:
        - handling error frames
        - handling unknown frames (not in DBC)
        Can be implemented using separate Notifier for these conditions.
        """
        self.tester = cantools.tester.Tester(
            bus_name=self.name,
            dut_name=self.dut_name,
            database=self.dbc,
            can_bus=self.interface.bus
        )

        try:
            self.uds_client = UdsClient(
                bus=self,
                isotp_layer=self.interface.isotp_layer,
                name=self.name,
                did_list=self.did_list
            )
            logger.info(f'CanBus: UdsClient created for bus {name}, '
                        f'address: {self.interface.isotp_layer.address}')
        except (TypeError, ValueError):
            # Don't implement IsoTP layer for the bus
            self.uds_client = None
            logger.info(f'CanBus: UdsClient not created for bus {name}')

        """
        Opt out of the internal Notifier of the Tester.
        Functionally of handling RX frames is be implemented in RxHandler.
        """
        self.tester._notifier.stop()

        self.rx_handler = RxHandler(
            bus=self.interface.bus,
            database=self.dbc,
            messages=self.tester.messages,
            on_message=on_message,
            uds_client=self.uds_client)

    def start_rx_handler(self):
        self.rx_handler.start()

    def stop_rx_handler(self):
        self.rx_handler.stop()

    def set_initial_values(self):
        for msg in self.tester.messages.values():
            msg._prepare_initial_signal_values()

    def start_restbus(self):
        self.tester.start()

        # inject error handler
        # TODO: implement this functionality in cantools Tester
        for m in self.tester.messages.values():
            task = m._periodic_task
            if task is not None and hasattr(task, 'on_error'):
                task.on_error = self.tx_error_handler

    def tx_error_handler(self, *args, **kwargs):
        self.interface.flush_tx_buffer()

        # continue sending
        return True

    def stop_restbus(self):
        self.tester.stop()

    def get_tx_messages(self):
        return [m for m in self.dbc.messages if is_not_sent_by(self.dut_name, m)]

    def set_signal_value(self, msg_name, signal_name, value):
        previous_value = self.get_signal_value(msg_name, signal_name)
        try:
            self._set_signal_value_internal(msg_name, signal_name, value)
        except (bitstruct.Error, cantools.Error):
            # bitstruct.Error: Cannot fit value in signal.
            # cantools.database.errors.EncodeError: Signal value is outside min/max range.
            # Revert data to previous value.
            self._set_signal_value_internal(msg_name, signal_name, previous_value)
            raise

    def _set_signal_value_internal(self, msg_name, signal_name, value):
        self.tester.messages[msg_name][signal_name] = value

    def get_signal_value(self, msg_name, signal_name):
        return self.tester.messages[msg_name][signal_name]
