import typing
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple

from udsoncan import DidCodec

from zalp.domain.canbus.diagnostic.utils import iterable_data_to_str


class DiagnosticSessionType(Enum):
    pass


class SupportedDiagnosticServices(Enum):
    DIAGNOSTIC_SESSION_CONTROL = auto()
    ECU_RESET = auto()
    READ_DATA_BY_IDENTIFIER = auto()
    READ_DTC_INFORMATION = auto()
    CLEAR_DIAGNOSTIC_INFORMATION = auto()


@dataclass(frozen=True)
class DiagnosticSubFunction:
    name: str
    service: SupportedDiagnosticServices
    # TODO: decide if int will be enough for every service here
    # for now it's:
    # - session - sesion type
    # - RDBI - DID to read
    # - DTC read - status mask
    # - DTC clear - status mask
    value: int
    data_list: list = field(init=False)
    data_str: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'data_list', self._calculate_data_list())
        object.__setattr__(self, 'data_str', self._calculate_data_str())

    def _calculate_data_list(self):
        match self.service:
            case SupportedDiagnosticServices.DIAGNOSTIC_SESSION_CONTROL:
                data = [0x10, self.value]
            case SupportedDiagnosticServices.ECU_RESET:
                data = [0x11, self.value]
            case SupportedDiagnosticServices.READ_DATA_BY_IDENTIFIER:
                data = [0x22, *self._value_to_int_byte_list(self.value)]
            case SupportedDiagnosticServices.READ_DTC_INFORMATION:
                subfunction = typing.cast(ReadDTCInformationSubFunction, self)
                data = [0x19, subfunction.value, subfunction.status_mask]
            case SupportedDiagnosticServices.CLEAR_DIAGNOSTIC_INFORMATION:
                data = [0x14, *self._value_to_int_byte_list(self.value)]
            case _:
                raise NotImplementedError
        return data

    def _value_to_int_byte_list(self, value):
        return list(value.to_bytes((value.bit_length() + 7) // 8, byteorder='big'))

    def _calculate_data_str(self):
        return iterable_data_to_str(self.data_list)


@dataclass(frozen=True)
class ReadDataByIdentifierSubFunction(DiagnosticSubFunction):
    did_codec: DidCodec


@dataclass(frozen=True)
class ReadDTCInformationSubFunction(DiagnosticSubFunction):
    status_mask: int


@dataclass
class DiagnosticService:
    name: str
    service: SupportedDiagnosticServices
    subfunctions: Tuple[DiagnosticSubFunction, ...]
