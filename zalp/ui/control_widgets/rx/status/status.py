import logging
import os
import time
from collections import defaultdict

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, NumericProperty

from zalp.application.concurrency import mainthread_once_per_frame
from zalp.ui import ZalpApp
from zalp.ui.colors import GREEN, RED
from zalp.ui.control_widgets.control_widget_base import HorizontalControlWidget

logger = logging.getLogger(__name__)

__filename = os.path.splitext(os.path.basename(__file__))[0] + '.kv'
__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, __filename))

TIMESTAMP_NOK_THRESHOLD = 0.4  # s
PERIOD_UPDATE_COMMS = 0.5  # s


class CameraStatusWidget(HorizontalControlWidget):
    vision_status = StringProperty('-')
    calibration_status = StringProperty('-')
    blockage_status = StringProperty('-')
    comms_status_text = StringProperty('NOK')

    last_update_timestamp = NumericProperty()
    update_comms_status_event = ObjectProperty()

    vision_status_color = defaultdict(
        lambda: RED,
        [
            ('Vision', GREEN),
            ('Not vision.', RED),
        ]
    )
    vision_status_text = defaultdict(
        lambda: '-',
        [
            ('Vision', 'OK'),
            ('Not vision.', 'NOK'),
        ]
    )

    calibration_blockage_status_color = defaultdict(
        lambda: RED,
        [
            ('OK', GREEN),
            ('NOK.', RED),
        ]
    )

    def start(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.camera_status.add_callback(self.update_camera_status)
        self.update_comms_status_event = Clock.schedule_interval(self.update_comms_status, PERIOD_UPDATE_COMMS)

    def stop(self, app: ZalpApp):
        Clock.unschedule(self.update_comms_status_event)
        app.backend.can_manager.signal_mapping.camera_status.remove_callback(self.update_camera_status)

    @mainthread_once_per_frame
    def update_camera_status(self, msg):
        self.vision_status = str(msg.PP_Vision_Status.get())
        self.calibration_status = str(msg.PP_Calibration_Status.get())
        self.blockage_status = str(msg.PP_Blockage_Status.get())
        self.last_update_timestamp = msg.last_update_timestamp

    def update_comms_status(self, _):
        self.comms_status_text = 'OK' if time.time() - self.last_update_timestamp < TIMESTAMP_NOK_THRESHOLD else 'NOK'
