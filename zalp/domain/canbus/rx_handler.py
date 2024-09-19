"""
Implementation based on cantools library.
https://github.com/cantools/cantools

The MIT License (MIT)

Copyright (c) 2015-2019 Erik Moqvist

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

import can

from .message import DecodedMessage

logger = logging.getLogger(__name__)


class Listener(can.Listener):
    def __init__(self, database, messages, on_message, uds_client):
        self._database = database
        self._messages = messages
        self._on_message = on_message
        self._uds_client = uds_client

    def on_message_received(self, msg):
        # TODO: TX frames probably also should be handled (for display purposes in application).
        #       Implement it somewhere else or refactor this class to be an
        #       all-around handler.
        if msg.is_error_frame or msg.is_remote_frame:
            # TODO: handle error frame
            return

        # If diagnostic msg, put to diag queue for IsoTP and UDS implementation to handle
        # TODO: maybe put only RX frames here, currently it puts all diag frames
        if self._uds_client is not None and self.is_diag_frame(msg):
            self._uds_client.put_rx_msg(msg)

        try:
            database_message = self._database.get_message_by_frame_id(
                msg.arbitration_id)
        except KeyError:
            logger.warning(f'can.Listener: Message not in DBC, ID {hex(msg.arbitration_id)}')
            # TODO: handle message not in DBC
            return

        # we can assume that unknown message is TX
        if msg.is_rx:
            direction = DecodedMessage.Direction.Rx
        else:
            direction = DecodedMessage.Direction.Tx

        message = self._messages[database_message.name]

        # if not message.enabled:
        #     return

        decoded = DecodedMessage(
            arbitration_id=msg.arbitration_id,
            timestamp=msg.timestamp,
            data=msg.data,
            direction=direction,
            name=database_message.name,
            signals=database_message.decode(msg.data,
                                            True,
                                            True),
            raw_signals=database_message.decode(msg.data,
                                                False,
                                                False))

        if self._on_message:
            self._on_message(decoded)

    def on_error(self, exc: Exception) -> None:
        """
        TODO: Log traceback if possible
        """
        logger.error(f'canbus: Error during frame reception: {exc}')

    def is_diag_frame(self, msg):
        address = self._uds_client.get_address()
        return msg.arbitration_id in (address.txid, address.rxid)


class RxHandler:
    """
    Class to handle RX messages on the CAN bus.
    - get and decode frames
    - call the callback function with the decoded message
    - handle error and unknown frames
    """

    def __init__(self,
                 bus,
                 database,
                 messages,
                 on_message,
                 uds_client):
        self._bus = bus
        self._database = database
        self._messages = messages
        self._on_message = on_message
        self._uds_client = uds_client

        self.listener = None
        self.notifier = None

    def start(self):
        # TODO: multiple calls will create duplicate notifiers
        self.listener = Listener(
            self._database,
            self._messages,
            self._on_message,
            self._uds_client
        )
        self.notifier = can.Notifier(self._bus, [self.listener])

    def stop(self):
        if self.notifier:
            self.notifier.stop()
