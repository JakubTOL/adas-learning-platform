"""
- services with their names
- subfunctions for each of these services, also with names
- how to differentiate?
"""
from zalp.domain.canbus import DiagnosticService, DiagnosticSubFunction, \
    SupportedDiagnosticServices, ReadDataByIdentifierSubFunction, DidCodec, ReadDTCInformationSubFunction


class DiagnosticSessionControlService(DiagnosticService):
    name = 'DiagnosticSessionControl (0x10)'
    service = SupportedDiagnosticServices.DIAGNOSTIC_SESSION_CONTROL
    subfunctions = (
        DiagnosticSubFunction(
            name='defaultSession (0x01)',
            service=service,
            value=0x01
        ),
        DiagnosticSubFunction(
            name='extendedDiagnosticSession (0x03)',
            service=service,
            value=0x03
        )
    )


DEFAULT_SESSION_SUBFUNCTION = filter(
    lambda s: s.value == 0x01, DiagnosticSessionControlService.subfunctions
).__next__()

EXTENDED_SESSION_SUBFUNCTION = filter(
    lambda s: s.value == 0x03, DiagnosticSessionControlService.subfunctions
).__next__()


class ReadDataByIdentifierService(DiagnosticService):
    name = 'ReadDataByIdentifier (0x22)'
    service = SupportedDiagnosticServices.READ_DATA_BY_IDENTIFIER
    subfunctions = (
        ReadDataByIdentifierSubFunction(
            name='ReadSoftwareVersion (F0 10)',
            service=service,
            value=0xF010,
            did_codec=DidCodec('2x14s')  # 2 bytes ID and 14 bytes ASCII string
        ),
    )


READ_SOFTWARE_VERSION_SUBFUNCTION = filter(
    lambda s: s.value == 0xF010, ReadDataByIdentifierService.subfunctions
).__next__()


class ReadDTCInformationService(DiagnosticService):
    name = 'ReadDTCInformation (0x19)'
    service = SupportedDiagnosticServices.READ_DTC_INFORMATION
    subfunctions = (
        ReadDTCInformationSubFunction(
            name='reportDTCByStatusMask (0x02)',
            service=service,
            # TODO: value unused in backend, reportDTCByStatusMask hardcoded in domain layer for now
            value=0x02,
            status_mask=0xFF
        ),
    )


READ_ALL_DTCS_SUBFUNCTION = filter(
    lambda s: s.value == 0x02 and s.status_mask == 0xFF, ReadDTCInformationService.subfunctions
).__next__()


class ClearDiagnosticInformationService(DiagnosticService):
    name = 'ClearDTCInformation (0x14)'
    service = SupportedDiagnosticServices.CLEAR_DIAGNOSTIC_INFORMATION
    subfunctions = (
        DiagnosticSubFunction(
            name='Clear all DTCs (0xFFFFFF)',
            service=service,
            # TODO: add group as a parameter
            value=0xFFFFFF
        ),
    )


CLEAR_ALL_DTCS_SUBFUNCTION = filter(
    lambda s: s.value == 0xFFFFFF, ClearDiagnosticInformationService.subfunctions
).__next__()

DIAGNOSTIC_SERVICES = (
    DiagnosticSessionControlService,
    ReadDataByIdentifierService,
    ReadDTCInformationService,
    ClearDiagnosticInformationService
)
