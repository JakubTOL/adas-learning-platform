import logging
import threading

from serial import LF

from .throttled_serial import ThrottledSerial

KORAD_SERIAL_TIMEOUT = 0.3

logger = logging.getLogger(__name__)


# TODO: Check if this class needs to be synchronized.
#       If all calls to this class which can collide are synchronized,
#       then probably not.
class KoradSerialInterface:
    def __init__(self, port='COM3', baudrate=9600):
        self.serial = ThrottledSerial(
            port=port,
            baudrate=baudrate,
            timeout=KORAD_SERIAL_TIMEOUT
        )

    # @synchronized
    def open(self):
        self.serial.open()
        logger.info(f'KoradSerialInterface: Serial port {self.serial.port} opened')

    # @synchronized
    def close(self):
        self.serial.close()
        logger.info(f'KoradSerialInterface: Serial port {self.serial.port} closed')

    # @synchronized
    def read_until(self, expected=LF, size=None):
        data = self.serial.read_until(expected, size)
        logger.debug(f'KoradSerialInterface: read_until, {expected=}, {size=}, received data {data}')
        return data

    # @synchronized
    def write(self, data):
        logger.debug(f'KoradSerialInterface: write, {data=}, thread {threading.get_ident()}')
        return self.serial.write(data)
