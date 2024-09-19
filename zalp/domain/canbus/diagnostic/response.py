import typing

import udsoncan
from udsoncan.services import DiagnosticSessionControl, ReadDataByIdentifier, ReadDTCInformation, \
    ClearDiagnosticInformation

from .services import DiagnosticSubFunction
from .utils import iterable_data_to_str


class Response:
    """
    Wrapper around udsoncan.Response, implementing additional functionalities.
    """

    def __init__(self,
                 response: udsoncan.Response,
                 subfunction: DiagnosticSubFunction):
        self._response = response
        self._subfunction = subfunction
        self._service = self._subfunction.service

        self._interpret_data()

    def _interpret_data(self):
        if not self._response.positive:
            self._interpreted_data = ''
            self._data_str = ''
            return
        data = self._response.service_data
        match data:
            case DiagnosticSessionControl.ResponseData() as t:
                data = typing.cast(t, data)
                interpreted_data = f'P2server_max = {data.p2_server_max} s; ' \
                                   f'P2*server_max = {data.p2_star_server_max} s'
            case ReadDataByIdentifier.ResponseData() as t:
                # TODO: asserts only 1 DID data is in the response.
                #       Refactor if more will be expected in one response.
                # TODO: implement handling multiple fields in the response, as well as
                #       how to differentiate between them
                data = typing.cast(t, data)
                interpreted_data = next(iter(data.values.values()))[0].decode()
            case ReadDTCInformation.ResponseData() as t:
                # TODO: add severity?
                data = typing.cast(t, data)
                interpreted_data = '\n'.join([f'DTC ID = 0x{dtc.id:X}, '
                                              f'Status = {hex(dtc.status.get_byte_as_int())}'
                                              for dtc in data.dtcs])
            case ClearDiagnosticInformation.ResponseData() as t:
                data = typing.cast(t, data)
                interpreted_data = ''
            case _:
                raise NotImplementedError
        self._interpreted_data = interpreted_data
        self._data_str = iterable_data_to_str(self.data)

    @property
    def interpreted_data(self):
        return self._interpreted_data

    @property
    def code(self):
        return self._response.code

    @property
    def code_name(self):
        return self._response.code_name

    @property
    def data(self):
        return self._response.data

    @property
    def service_data(self):
        return self._response.service_data

    @property
    def positive(self):
        return self._response.positive

    @property
    def data_str(self):
        return self._data_str

    @property
    def subfunction(self):
        return self._subfunction
