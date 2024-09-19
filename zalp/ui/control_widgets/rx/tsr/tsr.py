import logging
import os
from collections import defaultdict

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import StringProperty, ColorProperty

from zalp.application.concurrency import mainthread_once_per_frame
from zalp.ui import ZalpApp
from zalp.ui.colors import TRANSPARENT, GREEN, YELLOW
from zalp.ui.control_widgets.control_widget_base import HorizontalControlWidget
from zalp.ui.control_widgets.rx.tsr.tsr_dict import TSR_SIGN_NAME

logger = logging.getLogger(__name__)

__filename = os.path.splitext(os.path.basename(__file__))[0] + '.kv'
__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, __filename))


class TrafficSignWidget(HorizontalControlWidget):
    sign_name = StringProperty('-')
    sign_status = StringProperty('-')
    sign_name_color = ColorProperty(TRANSPARENT)
    sign_status_color = defaultdict(
        lambda: TRANSPARENT,
        [
            ('Invalid', TRANSPARENT),
            ('Visible', GREEN),
            ('Occluded', YELLOW),
            ('Out_Of_Image', YELLOW),
            ('Expelled', YELLOW),
        ]
    )
    sign_status_text = defaultdict(
        lambda: '-',
        [
            ('Invalid', 'Brak'),
            ('Visible', 'Widoczny'),
            ('Occluded', 'Zasłoniony'),
            ('Out_Of_Image', 'Poza widokiem'),
            ('Expelled', 'Historyczny'),
        ]
    )

    def start(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.tsr_0.add_callback(self.update_sign_data)

    def stop(self, app: ZalpApp):
        app.backend.can_manager.signal_mapping.tsr_0.remove_callback(self.update_sign_data)

    # TODO: if signal values did not change, we can potentially skip the UI update.
    #       Will this increase performance, or does the set operation is not high cost
    #       if no re-draw is requested?
    @mainthread_once_per_frame
    def update_sign_data(self, msg):
        sign_status = msg.PP_TSR_Sign_Status_0.get()
        if sign_status == 'Invalid':
            sign_name = 'Brak wykrytego znaku'
            sign_name_color = TRANSPARENT
        else:
            sign_name = TSR_SIGN_NAME.get(msg.PP_TSR_Sign_Name_0.get(), "Niepoprawny znak")
            sign_name_color = GREEN
        self.sign_name = str(sign_name)
        self.sign_name_color = sign_name_color
        self.sign_status = str(sign_status)
