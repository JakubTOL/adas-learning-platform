import logging
from enum import IntFlag, auto

from wrapt import synchronized

from . import utils
from .exceptions import KoradIncorrectResponseException
from .failsafe import failsafe

logger = logging.getLogger(__name__)

DEFAULT_VOLTAGE = 13.7


class Korad:
    """
    Class implementing Korad power supply.


    All of methods interacting with the serial interface
    are synchronized with shared lock.
    This is because every interaction with serial interface (either read + write or read only)
    can interfere with each other.

    "synchronized" needs to be the outer decorator, while "failsafe" needs to be the inner decorator.
    Otherwise, the lock is not bound properly to the class instance.
    """

    class Status(IntFlag):
        CH1_STATE = auto()
        CH2_STATE = auto()
        TRACKING_2 = auto()
        TRACKING_3 = auto()
        BEEP = auto()
        LOCK = auto()
        OUTPUT = auto()
        NOT_USED_7 = auto()

        @classmethod
        def from_char(cls, char):
            """
            Create KoradStatus from character received from interface.
            Example:
                Korad.Status.from_char('Q')
                Returns Status.CH1_STATE|BEEP|OUTPUT: 81
            """
            flag = ord(char)
            return cls(flag)

        @property
        def beep(self):
            return bool(self & self.__class__.BEEP)

        @property
        def lock(self):
            return bool(self & self.__class__.LOCK)

        @property
        def output(self):
            return bool(self & self.__class__.OUTPUT)

    def __init__(self, interface):
        self.interface = interface
        self._consecutive_failures = 0
        self._failsafe_enabled = True

    @synchronized
    def connect(self, voltage=DEFAULT_VOLTAGE, do_selftest=True):
        self.interface.close()
        self.interface.open()
        if do_selftest:
            self.selftest()
        self.set_output(False)
        self.set_voltage(voltage)

    @synchronized
    @failsafe
    def selftest(self):
        self.interface.write('*IDN?'.encode())
        id_str = self.interface.read_until(b'\0').decode()
        if 'KORAD' not in id_str:
            logger.error(f'Korad: selftest NOK, response: {id_str}')
            raise KoradIncorrectResponseException(f'Korad: incorrect self-test response: {id_str}')
        logger.debug(f'Korad: selftest OK, response: {id_str}')

    @synchronized
    @failsafe
    def get_voltage(self):
        try:
            self.interface.write('VSET1?'.encode())
            read_str = self.interface.read_until(size=5)
            read_float = float(read_str)
            logger.debug(f'Korad: Voltage read: {read_float}')
            return read_float
        except ValueError as e:
            raise KoradIncorrectResponseException('Incorrect voltage received') from e

    @synchronized
    @failsafe
    def set_voltage(self, voltage=None):
        if voltage is None:
            voltage = DEFAULT_VOLTAGE
        if not utils.voltage_ok(voltage):
            raise ValueError('Incorrect voltage provided')

        voltage_formatted = utils.voltage_format(voltage)
        data = 'VSET1:' + voltage_formatted
        self.interface.write(data.encode())
        logger.debug(f'Korad: Voltage set: {voltage}')

    @synchronized
    @failsafe
    def get_output(self):
        status = self._read_status()
        on = status.output
        logger.debug(f'Korad: Output get {"ON" if on else "OFF"}')
        return on

    @synchronized
    @failsafe
    def set_output(self, on):
        data = 'OUT' + ('1' if on else '0')
        self.interface.write(data.encode())
        logger.debug(f'Korad: Output set {"ON" if on else "OFF"}')

    @synchronized
    @failsafe
    def get_current(self):
        try:
            data = 'IOUT1?'
            self.interface.write(data.encode())
            read_str = self.interface.read_until(size=5)
            read_float = float(read_str)
            logger.debug(f'Korad: Current: {read_float}')
            return read_float
        except ValueError as e:
            raise KoradIncorrectResponseException('Incorrect current received') from e

    @synchronized
    @failsafe
    def _read_status(self):
        try:
            data = 'STATUS?'
            self.interface.write(data.encode())
            read_str = self.interface.read_until(size=1)
            return Korad.Status.from_char(read_str)
        except TypeError as e:
            raise KoradIncorrectResponseException('Incorrect status received') from e
