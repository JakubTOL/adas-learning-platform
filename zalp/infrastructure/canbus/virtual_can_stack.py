"""
Code based on python-can-isotp library.
https://github.com/pylessard/python-can-isotp

MIT License

Copyright (c) 2017 Pier-Yves Lessard

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
import queue

from isotp import TransportLayer, CanMessage

logger = logging.getLogger(__name__)


class VirtualCanStack(TransportLayer):
    """
    The IsoTP transport using `python-can <https://python-can.readthedocs.io>`_ as CAN layer. python-can must be installed in order to use this class.
    All parameters except the ``bus`` parameter will be given to the :class:`TransportLayer<isotp.TransportLayer>` constructor

    :param bus: A python-can bus object implementing ``recv`` and ``send``
    :type bus: BusABC

    :param address: The address information of CAN messages. Includes the addressing mode, txid/rxid, source/target address and address extension. See :class:`isotp.Address<isotp.Address>` for more details.
    :type address: isotp.Address

    :param error_handler: A function to be called when an error has been detected. An :class:`isotp.protocol.IsoTpError<isotp.protocol.IsoTpError>` (inheriting Exception class) will be given as sole parameter
    :type error_handler: Callable

    :param params: List of parameters for the transport layer
    :type params: dict

    """

    def _tx_canbus_3plus(self, msg):
        self.bus.send(can.Message(arbitration_id=msg.arbitration_id, data=msg.data, is_extended_id=msg.is_extended_id,
                                  is_fd=msg.is_fd, bitrate_switch=msg.bitrate_switch))

    def _tx_canbus_3minus(self, msg):
        self.bus.send(can.Message(arbitration_id=msg.arbitration_id, data=msg.data, extended_id=msg.is_extended_id,
                                  is_fd=msg.is_fd, bitrate_switch=msg.bitrate_switch))

    def rx_canbus(self):
        try:
            msg = self._rx_queue.get(block=False)
            return msg
        except queue.Empty:
            pass

    def __init__(self, bus, *args, **kwargs):
        self._rx_queue = queue.Queue()
        self.bus = None
        global can
        import can

        # Backward compatibility stuff.
        message_input_args = can.Message.__init__.__code__.co_varnames[:can.Message.__init__.__code__.co_argcount]
        if 'is_extended_id' in message_input_args:
            self.tx_canbus = self._tx_canbus_3plus
        else:
            self.tx_canbus = self._tx_canbus_3minus

        self.set_bus(bus)
        TransportLayer.__init__(self, rxfn=self.rx_canbus, txfn=self.tx_canbus, *args, **kwargs)

    def set_bus(self, bus):
        if not isinstance(bus, can.BusABC):
            raise ValueError('bus must be a python-can BusABC object')
        self.bus = bus

    def put_rx_msg(self, msg):
        return self._rx_queue.put_nowait(msg)
