from .can_bus_manager import CanBusManager
from .diagnostic import ReadDataByIdentifierService
from .signal_mapping import SignalMapping
from ..concurrency import run_in_thread


class CanManager:
    def __init__(self):
        self.can1 = CanBusManager(
            name='VEHICLE_CAN',
            dbc_path='dbc\\VEHICLE_CAN.dbc',
            on_message=self.on_message,
            did_list=ReadDataByIdentifierService.subfunctions)
        # self.can2 = CanBusManager(
        #     name='CAN2',
        #     dbc_path='dbc\\RNA_ITS-CAN.dbc')

        self.signal_mapping = SignalMapping(
            can1=self.can1
        )

        self.callbacks = []

    def start_rx_handler(self):
        self.can1.start_rx_handler()

    def stop_rx_handler(self):
        self.can1.stop_rx_handler()

    def start_restbus(self):
        self.can1.start_restbus()

    def stop_restbus(self):
        self.can1.stop_restbus()

    def shutdown(self):
        self.can1.shutdown()

    def set_default_values(self):
        self.can1.bus.set_initial_values()

    def set_initialization_values(self):
        self.signal_mapping.set_initialization_values()

    @run_in_thread
    def on_message(self, msg):
        self.signal_mapping.on_message(msg)
        for callback in self.callbacks:
            callback(msg)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)