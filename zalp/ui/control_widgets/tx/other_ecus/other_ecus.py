import logging
import os

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton

from zalp.application.concurrency import run_in_thread
from zalp.ui import ZalpApp
from zalp.ui.control_widgets.control_widget_base import HorizontalControlWidget

logger = logging.getLogger(__name__)

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'other_ecus.kv'))


class OtherEcusWidget(HorizontalControlWidget):
    bcm_status_choice_widget = ObjectProperty()
    acc_status_choice_widget = ObjectProperty()
    abs_status_choice_widget = ObjectProperty()

    def start(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.bcm_status.add_set_callback(self.update_bcm_status)
        app.backend.can_manager.signal_mapping.acc_status.add_set_callback(self.update_acc_status)
        app.backend.can_manager.signal_mapping.abs_status.add_set_callback(self.update_abs_status)

    def stop(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.bcm_status.remove_set_callback(self.update_bcm_status)
        app.backend.can_manager.signal_mapping.acc_status.remove_set_callback(self.update_acc_status)
        app.backend.can_manager.signal_mapping.abs_status.remove_set_callback(self.update_abs_status)

    @run_in_thread
    def set_bcm_status(self, app: ZalpApp, status):
        signal = app.backend.can_manager.signal_mapping.bcm_status
        if signal.get() == status:
            return
        signal.set(status)

    @run_in_thread
    def set_acc_status(self, app: ZalpApp, status):
        signal = app.backend.can_manager.signal_mapping.acc_status
        if signal.get() == status:
            return
        signal.set(status)

    @run_in_thread
    def set_abs_status(self, app: ZalpApp, status):
        signal = app.backend.can_manager.signal_mapping.abs_status
        if signal.get() == status:
            return
        signal.set(status)

    @mainthread
    def update_bcm_status(self, status):
        self.bcm_status_choice_widget.update(status)

    @mainthread
    def update_acc_status(self, status):
        self.acc_status_choice_widget.update(status)

    @mainthread
    def update_abs_status(self, status):
        self.abs_status_choice_widget.update(status)


class EcuStatusChoiceWidget(BoxLayout):
    not_present_button: ToggleButton = ObjectProperty()
    ok_button: ToggleButton = ObjectProperty()
    fail_button: ToggleButton = ObjectProperty()

    def update(self, status):
        match status:
            case 'Not Present':
                self.not_present_button.state = 'down'
            case 'OK':
                self.ok_button.state = 'down'
            case 'Fail':
                self.fail_button.state = 'down'
            case _:
                logger.error('EcuStatusChoiceWidget: Incorrect status value provided')
