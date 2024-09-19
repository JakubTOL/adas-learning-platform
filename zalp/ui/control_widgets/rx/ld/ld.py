import logging
import os
from collections import defaultdict

from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

from zalp.ui import ZalpApp
from zalp.ui.colors import RED, ORANGE, GREEN
from zalp.ui.control_widgets.control_widget_base import HorizontalControlWidget

logger = logging.getLogger(__name__)

__filename = os.path.splitext(os.path.basename(__file__))[0] + '.kv'
__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, __filename))


class MeterLabelWidget(BoxLayout):
    value_text = StringProperty('-')
    direction_left = BooleanProperty()

    def update(self, value):
        if value in (0.0, 30.0, 40.0):
            self.value_text = '-'
            return
        # Multiply by -1 if value is coming from left line
        if self.direction_left:
            value *= -1
        self.value_text = f'{value:.2f}'  # 2 decimal places


class LineWidget(Widget):
    value = NumericProperty(0)
    line_color = defaultdict(
        lambda: GREEN,  # OK
        [
            (0, ORANGE),  # not detected
            (30.0, RED),  # fail
            (40.0, ORANGE),  # turned off
        ]
    )

    def update(self, value):
        self.value = value


class SteeringWheelWidget(Widget):
    value_left = NumericProperty(0)
    value_right = NumericProperty(0)

    def get_steering_wheel_color(self, value_left, value_right):
        if value_left == 40.0 or value_right == 40.0:
            return ORANGE  # turned off
        elif value_left == 30.0 or value_right == 30.0:
            return RED  # fail
        else:  # OK
            return GREEN

    def update(self, value_left, value_right):
        self.value_left = value_left
        self.value_right = value_right


class LineDetectionWidget(HorizontalControlWidget):
    left_meter_label = ObjectProperty()
    left_line_widget = ObjectProperty()
    steering_wheel_widget = ObjectProperty()
    right_line_widget = ObjectProperty()
    right_meter_label = ObjectProperty()

    def start(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.line_volt_data.add_callback(self.update)

    def stop(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.line_volt_data.remove_callback(self.update)

    def update(self, msg):
        value_left = msg.PP_LeftLineDistance.get()
        value_right = msg.PP_RightLineDistance.get()
        self.left_meter_label.update(value_left)
        self.left_line_widget.update(value_left)
        self.steering_wheel_widget.update(value_left, value_right)
        self.right_line_widget.update(value_right)
        self.right_meter_label.update(value_right)
