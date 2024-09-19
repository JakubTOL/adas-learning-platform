from abc import ABC
from dataclasses import dataclass, field

from zalp.application.canbus.can_bus_manager import CanBusManager


@dataclass
class Signal(ABC):
    """
    Class representing CAN signal.

    Implements getting and setting the value, as well as callbacks when the value is set
    - useful to register UI update when signal is set outside of the UI.

    # TODO: Refactor for for complex enumeration signals with choices.
    #       We probably want to pass to UI full choice list, which is then used by the UI
    #       to send the correct value to set.
    """
    mgr: CanBusManager
    msg_name: str
    signal_name: str
    _set_callbacks: list = field(default_factory=list)

    def get(self):
        return self.mgr.get_signal_value(self.msg_name,
                                         self.signal_name)

    def set(self, value):
        self.mgr.set_signal_value(self.msg_name,
                                  self.signal_name,
                                  value)
        for callback in self._set_callbacks:
            callback(value)

    def add_set_callback(self, callback):
        self._set_callbacks.append(callback)

    def remove_set_callback(self, callback):
        self._set_callbacks.remove(callback)
