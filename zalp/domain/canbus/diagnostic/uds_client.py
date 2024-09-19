import logging
import typing
from threading import RLock, Event
from typing import Iterable

import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
from wrapt import synchronized

from zalp.application.concurrency import run_in_thread
from .exceptions import TimeoutException
from .response import Response
from .services import DiagnosticSubFunction, SupportedDiagnosticServices, ReadDataByIdentifierSubFunction, \
    ReadDTCInformationSubFunction

logger = logging.getLogger(__name__)


class TesterPresentService:
    def __init__(self, uds_client):
        self._uds_client = uds_client
        self._active = False
        self._stop_event = Event()
        self._period = 1  # s
        self._set_callbacks = []
        self._thread = None

    @run_in_thread
    def run(self):
        logger.info('TesterPresentService: Starting')
        while True:
            try:
                if self._active:
                    self._uds_client.send_tester_present()
                cancelled = self._stop_event.wait(self._period)
            # TODO: add other exceptions handling here that might happen during sending TesterPresent
            except udsoncan.TimeoutException:
                cancelled = self._stop_event.wait(self._period)
                pass
            if cancelled:
                break
        self._stop_event.clear()
        self._thread = None
        logger.info('TesterPresentService: Stopping')

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, on):
        self._active = on
        for callback in self._set_callbacks:
            callback(on)

    def add_set_callback(self, callback):
        self._set_callbacks.append(callback)

    def remove_set_callback(self, callback):
        self._set_callbacks.remove(callback)

    def start(self):
        if self._thread:
            raise ValueError('TesterPresentService is already running')
        self._thread = self.run()

    def stop(self):
        self._stop_event.set()


class UdsClient:
    def __init__(self,
                 bus,
                 isotp_layer,
                 name,
                 did_list: Iterable[ReadDataByIdentifierSubFunction]
                 ):
        self._bus = bus
        self._name = name
        self._did_list = did_list

        self._isotp_layer = isotp_layer

        # TODO: implement new virtual bus for this connection.
        #       send is the same, RX should be put in the RxHandler
        self._connection = PythonIsoTpConnection(
            self._isotp_layer,
            name=self._name
        )

        data_identifiers = {sf.value: sf.did_codec for sf in did_list}
        # TODO: Logger of Client is not constructing logs according to our convention.
        #       Maybe disable it and log everything that is relevant in this class?
        self._client = Client(
            conn=self._connection,
            config={
                'use_server_timing': False,  # Causes timeouts otherwise,
                # Probably caused by timing deviation on our side
                'data_identifiers': data_identifiers,
                'exception_on_negative_response': False  # Handled by user code normally to display the response
            }
        )
        self._client.open()

        self._tester_present_service = TesterPresentService(self)
        self._lock = RLock()

    def get_address(self):
        return self._isotp_layer.address

    def put_rx_msg(self, msg):
        return self._isotp_layer.put_rx_msg(msg)

    def set_tester_present(self, on):
        self._tester_present_service.active = on

    def get_tester_present(self) -> bool:
        return self._tester_present_service.active

    def add_tester_present_set_callback(self, callback):
        self._tester_present_service.add_set_callback(callback)

    def remove_tester_present_set_callback(self, callback):
        self._tester_present_service.remove_set_callback(callback)

    @synchronized
    def send_diagnostic_request(self, subfunction: DiagnosticSubFunction):
        # TODO: use library functions here or send manually?
        #       we can use DiagnosticSubFunction.get_data(), it's needed for UI anyways
        try:
            match subfunction.service:
                case SupportedDiagnosticServices.DIAGNOSTIC_SESSION_CONTROL:
                    if subfunction.value != udsoncan.client.services.DiagnosticSessionControl.Session.defaultSession:
                        self.set_tester_present(True)
                    response = self._client.change_session(subfunction.value)
                case SupportedDiagnosticServices.READ_DATA_BY_IDENTIFIER:
                    response = self._client.read_data_by_identifier(subfunction.value)
                case SupportedDiagnosticServices.READ_DTC_INFORMATION:
                    subfunction = typing.cast(ReadDTCInformationSubFunction, subfunction)
                    response = self._client.get_dtc_by_status_mask(subfunction.status_mask)
                case SupportedDiagnosticServices.CLEAR_DIAGNOSTIC_INFORMATION:
                    response = self._client.clear_dtc(subfunction.value)
                case _:
                    raise NotImplementedError(f'Sending of service {subfunction.service} is not implemented')
            return Response(response,
                            subfunction)
        except udsoncan.TimeoutException as e:
            raise TimeoutException('No response from the ECU') from e

    @synchronized
    def send_tester_present(self):
        self._client.tester_present()

    def start_tester_present_service(self):
        self._tester_present_service.start()

    def stop_tester_present_service(self):
        self._tester_present_service.stop()
