import logging
from dataclasses import dataclass, field
from typing import Iterable

from zalp.application.canbus.can_bus_manager import CanBusManager
from zalp.domain.canbus import DecodedMessage
from .signal import Signal

logger = logging.getLogger(__name__)


@dataclass
class Message:
    mgr: CanBusManager
    name: str
    # If rx is True, callbacks will be performed when message is "received"
    rx: bool
    signal_names: Iterable[str]
    last_update_timestamp: float = 0
    _signals: dict[str, Signal] = field(default_factory=dict)
    _callbacks: list = field(default_factory=list)

    def __post_init__(self):
        for name in self.signal_names:
            self._signals[name] = Signal(
                mgr=self.mgr,
                msg_name=self.name,
                signal_name=name
            )

    def __getattr__(self, item):
        return self._signals[item]

    def on_message(self, received_msg: DecodedMessage):
        if not self.rx:
            # If rx is False, callbacks will not be performed.
            # Tx frames received on CAN are not used to update the widgets.
            # If value of a signal is changed in the program,
            # set callback will be triggered, which can update the UI.
            return
        for name, value in received_msg.signals.items():
            self._on_signal(name, value)
        self.last_update_timestamp = received_msg.timestamp
        for callback in self._callbacks:
            callback(self)

    def _on_signal(self, name, value):
        try:
            self._signals[name].set(value)
        except KeyError:
            logger.warning(f'SignalMapping: Tried to set signal non-existing signal in message {self.name}')
            pass

    def add_callback(self, callback):
        if not self.rx:
            raise ValueError('Message callbacks for Tx frames are not allowed - use signal callbacks instead')
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        if not self.rx:
            raise ValueError('Message callbacks for Tx frames are not allowed - use signal callbacks instead')
        self._callbacks.remove(callback)


class Messages:
    def __init__(self):
        self._messages = dict()

    def add_message(self, msg: Message):
        self._messages[msg.name] = msg

    def __getattr__(self, item):
        return self._messages[item]

    def on_message(self, received_msg: DecodedMessage):
        try:
            self._messages[received_msg.name].on_message(received_msg)
        except KeyError:
            # frame not mapped, ignore
            pass
