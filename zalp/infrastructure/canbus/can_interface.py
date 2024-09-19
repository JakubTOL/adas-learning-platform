import ctypes
import logging
import os
import typing

import can
import isotp
from can.interfaces.vector import xlclass, xldefine

from .exceptions import CanInterfaceNotImplementedError, CanInitializationError
from .virtual_can_stack import VirtualCanStack

logger = logging.getLogger(__name__)


# TODO: all of CAN sending/receiving could be refactored using multiprocessing
#       if threading-based approach will not result in acceptable performance

class CanInterface:
    def __init__(self, name):
        try:
            bus = can.ThreadSafeBus(
                context=name,
                receive_own_messages=True
            )
            # TODO: extremely ugly workaround for found issue with ThreadSafeBus - `send` is not synchronized
            #       when called from inside the library.
            #       Replace dummy lock with the lock for `send` method.
            #       https://github.com/hardbyte/python-can/issues/1620
            bus.__wrapped__._lock_send_periodic = bus._lock_send
            bus.flush_tx_buffer()
            self.bus = typing.cast(can.BusABC, bus)
            self._init_uds(name)

        # CanInterfaceNotImplementedError when bus is not correct
        # TypeError when channel is incorrect
        except (can.exceptions.CanInterfaceNotImplementedError, TypeError) as e:
            raise CanInterfaceNotImplementedError(
                'Cannot initialize CAN bus. '
                'Environmental variables might not be set correctly.') from e
        except can.exceptions.CanInitializationError as e:
            raise CanInitializationError(
                'Cannot initialize CAN bus. '
                'Interface might not be connected.'
            )

        # self.periodic_tasks = []

    def _init_uds(self, name):
        try:
            address = isotp.Address(
                txid=int(os.getenv('CAN_UDS_TXID_' + name), 0),
                rxid=int(os.getenv('CAN_UDS_RXID_' + name), 0),
            )
            self.isotp_layer = VirtualCanStack(
                bus=self.bus,
                address=address,
                error_handler=self.uds_error_handler,
                params={
                    'tx_padding': 0,
                    'squash_stmin_requirement': True
                }
            )

            # Override sleep timing inside ISO-TP implementation.
            # Debugging showed that "WAIT_FC" state might not be respected properly - replace with 10 ms to be sure.
            # TODO: implementation should not be polling, just block until events are available to be processed
            self.isotp_layer.set_sleep_timing(
                idle=0.01,
                wait_fc=0.01
            )
        except (TypeError, ValueError):
            # no correct ID provided, don't implement IsoTP layer for the bus
            self.isotp_layer = None

    def shutdown(self):
        self.bus.shutdown()

    def flush_tx_buffer(self):
        """
        Implementation specific for Vector HW.
        Created because VectorBus.flush_tx_buffer works only for XL-series family.
        """
        mask = self.bus.mask
        xl_event = xlclass.XLevent()
        xl_event.tag = xldefine.XL_EventTags.XL_TRANSMIT_MSG
        xl_event.tagData.msg.flags |= xldefine.XL_MessageFlags.XL_CAN_MSG_FLAG_OVERRUN

        self.bus.xldriver.xlCanTransmit(
            self.bus.port_handle, mask, ctypes.c_uint(1), xl_event
        )

    def uds_error_handler(self, error):
        logger.error(f'CanInterface: Error during UDS handling: {error}')

    # def send_periodic(self, msgs, period):
    #     task = self.bus.send_periodic(msgs, period)
    #     self.periodic_tasks.append(task)
