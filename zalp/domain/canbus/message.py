from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any


@dataclass
class DecodedMessage:
    """
    Class representing decoded CAN message.
    """

    class Direction(Enum):
        Rx = auto()
        Tx = auto()

    arbitration_id: int
    timestamp: float
    direction: Direction
    data: bytearray
    name: str
    signals: Dict[str, Any]  # signal name, signal value
    # TODO: remove if unused
    raw_signals: Dict[str, int]  # signal name, signal value


class DecodedMessages(Dict):
    def update_message(self, msg: DecodedMessage):
        self[msg.arbitration_id] = msg
