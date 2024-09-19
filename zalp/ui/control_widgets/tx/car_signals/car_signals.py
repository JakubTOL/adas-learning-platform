import logging
import os

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from zalp.application.concurrency import run_in_thread, mainthread_once_per_frame
from zalp.ui import ZalpApp
from zalp.ui.control_widgets.control_widget_base import HorizontalControlWidget
from zalp.ui.control_widgets.snackbar import ScenarioSnackbar
from zalp.ui.control_widgets.tx.Gauge import Gauge

logger = logging.getLogger(__name__)

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'car_signals.kv'))


class CarSignalsWidget(HorizontalControlWidget):
    car_speed_input = ObjectProperty(None)
    gauge: Gauge = ObjectProperty(None)
    car_speed_valid_checkbox = ObjectProperty(None)
    car_lines_enabled_checkbox = ObjectProperty(None)

    def start(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.car_speed.add_set_callback(self.update_car_speed)
        app.backend.can_manager.signal_mapping.car_speed_valid.add_set_callback(self.update_car_speed_valid)
        app.backend.can_manager.signal_mapping.car_lines_enabled.add_set_callback(self.update_car_lines_enabled)

    def stop(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.car_speed.remove_set_callback(self.update_car_speed)
        app.backend.can_manager.signal_mapping.car_speed_valid.remove_set_callback(self.update_car_speed_valid)
        app.backend.can_manager.signal_mapping.car_lines_enabled.remove_set_callback(self.update_car_lines_enabled)

    @run_in_thread
    def set_car_speed(self, app: ZalpApp):
        car_speed = app.backend.can_manager.signal_mapping.car_speed
        try:
            speed = float(self.car_speed_input.text)
            car_speed.set(speed)
        except Exception:
            self.update_car_speed(car_speed.get())
            ScenarioSnackbar(text='Nieprawidłowa prędkość samochodu').open()
            raise

    @mainthread_once_per_frame
    def update_car_speed(self, speed):
        self.car_speed_input.text = str(speed)
        self.gauge.DataUpdate(speed)

    @run_in_thread
    def set_car_speed_valid(self, app: ZalpApp):
        valid = self.car_speed_valid_checkbox.active
        app.backend.can_manager.signal_mapping.car_speed_valid.set(valid)

    @mainthread_once_per_frame
    def update_car_speed_valid(self, valid):
        self.car_speed_valid_checkbox.active = valid

    # TODO: Frontend contains information on how to map the value ("lines enabled" == 10)
    #       Ideally frontend should only have bool flag. This choice should be coded
    #       as an enumeration in the DBC, instead.

    @run_in_thread
    def set_car_lines_enabled(self, app: ZalpApp):
        enabled = self.car_lines_enabled_checkbox.active
        app.backend.can_manager.signal_mapping.car_lines_enabled.set(10 if enabled else 0)

    @mainthread_once_per_frame
    def update_car_lines_enabled(self, value):
        self.car_lines_enabled_checkbox.active = value == 10
