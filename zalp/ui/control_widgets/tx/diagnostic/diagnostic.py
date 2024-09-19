import datetime
import logging
import os
import time
from collections import defaultdict
from enum import Enum, auto

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.treeview import TreeViewNode

from zalp.application.canbus import DIAGNOSTIC_SERVICES
from zalp.application.canbus import DiagnosticService, DiagnosticSubFunction, TimeoutException
from zalp.application.concurrency import run_in_thread
from zalp.ui import ZalpApp
from zalp.ui.colors import RED, GREEN, ORANGE
from zalp.ui.control_widgets.control_widget_base import ControlWidget

logger = logging.getLogger(__name__)

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'diagnostic.kv'))


class DiagnosticServiceNode(TreeViewNode, BoxLayout):
    def __init__(self, service: DiagnosticService, **kwargs):
        self.service = service
        self.name = self.service.name
        super().__init__(**kwargs)


class DiagnosticSubFunctionNode(TreeViewNode, BoxLayout):
    def __init__(self, subfunction: DiagnosticSubFunction, **kwargs):
        self.subfunction = subfunction
        self.name = self.subfunction.name
        super().__init__(**kwargs)


class SelectedSubfunctionDetailsView(GridLayout):
    selected_subfunction = ObjectProperty()
    pass


class DiagnosticServicesScrollView(ScrollView):
    tree = ObjectProperty()
    selected_subfunction = ObjectProperty()

    def populate(self):
        for service in DIAGNOSTIC_SERVICES:
            service_node = DiagnosticServiceNode(service)
            self._add_service(service_node)

    # def get_selected_subfunction(self):
    #     node = self.tree.selected_node
    #     return node.subfunction if node else None

    def _add_service(self, service_node: DiagnosticServiceNode):
        self.tree.add_node(service_node)
        for subfunction in service_node.service.subfunctions:
            subfunction_node = DiagnosticSubFunctionNode(subfunction)
            self.tree.add_node(subfunction_node, service_node)


class UdsLogEntry(TreeViewNode, GridLayout):
    class Direction(Enum):
        TX = auto()
        RX = auto()

    class Status(Enum):
        OK = auto()
        NEGATIVE = auto()
        ERROR = auto()

    entry_color = defaultdict(
        lambda: RED,
        [
            (Status.OK, GREEN),
            (Status.NEGATIVE, ORANGE),
            (Status.ERROR, RED),
        ]
    )

    def __init__(self,
                 timestamp: str,
                 direction: Direction,
                 name: str,
                 data: str,
                 interpreted_data: str,
                 status: Status):
        self.timestamp = timestamp
        self.direction = direction
        self.name = name
        self.data = data
        self.interpreted_data = interpreted_data
        self.status = status
        super().__init__()


def _get_formatted_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S:%f')


class UdsLogScrollView(ScrollView):
    layout: GridLayout = ObjectProperty()

    @mainthread
    def add_entry(self,
                  direction,
                  name,
                  data='',
                  interpreted_data='',
                  status=UdsLogEntry.Status.OK):
        timestamp = _get_formatted_timestamp(time.time())
        entry = UdsLogEntry(
            timestamp=timestamp,
            direction=direction,
            name=name,
            data=data,
            interpreted_data=interpreted_data,
            status=status
        )
        self.layout.add_widget(entry)
        self._scroll_to_bottom_after_added()

    @mainthread
    def _scroll_to_bottom_after_added(self):
        """
        Scroll to the bottom after entry was added.
        Implemented using `mainthread` decorator,
        so it will be executed after the layout update (and take the new entry into account).
        """
        if self.height < self.layout.height:
            # Content is larger than the scroll view.
            # Scroll to the bottom to see the last request.
            self.scroll_y = 0

    def clear_entries(self):
        self.layout.clear_widgets()
        # scroll to the top
        self.scroll_y = 1


class DiagnosticWidget(ControlWidget, GridLayout):
    services_scroll_view: DiagnosticServicesScrollView = ObjectProperty()
    uds_log_scroll_view: UdsLogScrollView = ObjectProperty()
    request_in_progress = BooleanProperty(False)
    tester_present_active_checkbox: CheckBox = ObjectProperty()

    def start(self, app: ZalpApp):
        app.backend.can_manager.can1.bus.uds_client.start_tester_present_service()
        app.backend.can_manager.can1.bus.uds_client.add_tester_present_set_callback(self.update_tester_present)

    def stop(self, app: ZalpApp):
        app.backend.can_manager.can1.bus.uds_client.stop_tester_present_service()
        app.backend.can_manager.can1.bus.uds_client.remove_tester_present_set_callback(self.update_tester_present)

    def populate(self):
        self.services_scroll_view.populate()

    @mainthread
    def update_tester_present(self, on):
        self.tester_present_active_checkbox.active = on

    @run_in_thread
    def send_request(self, app: ZalpApp):
        subfunction = self.services_scroll_view.selected_subfunction
        if subfunction is None:
            # should never happen, button is disabled if no sub-function is selected
            return
        if self.request_in_progress:
            # should also never happen, because button is disabled
            # safeguard implemented to not ever send a request when we're waiting for a response.
            return
        # TODO: refactor logging of these entries
        self.uds_log_scroll_view.add_entry(
            direction=UdsLogEntry.Direction.TX,
            name=subfunction.name,
            data=subfunction.data_str,
        )
        self._send_request_internal(app, subfunction)

    def _send_request_internal(self, app, subfunction):
        direction = UdsLogEntry.Direction.RX
        try:
            self.request_in_progress = True
            response = app.backend.can_manager.can1.send_diagnostic_request(subfunction)
        except TimeoutException:
            self.uds_log_scroll_view.add_entry(
                direction=direction,
                name='No response',
                status=UdsLogEntry.Status.ERROR,
            )
            raise
        except Exception:
            self.uds_log_scroll_view.add_entry(
                direction=direction,
                name='Error',
                status=UdsLogEntry.Status.ERROR
            )
            raise
        finally:
            self.request_in_progress = False
        self.uds_log_scroll_view.add_entry(
            direction=direction,
            name=response.code_name,
            data=response.data_str,
            interpreted_data=response.interpreted_data,
            status=UdsLogEntry.Status.OK if response.positive else UdsLogEntry.Status.NEGATIVE
        )

    @run_in_thread
    def set_tester_present(self, app: ZalpApp):
        app.backend.can_manager.can1.set_tester_present(self.tester_present_active_checkbox.active)
