import os

from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty

from zalp.ui import ZalpApp
from zalp.ui.control_widgets.control_widget_base import HorizontalControlWidget

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'psu.kv'))


class PsuControlWidget(HorizontalControlWidget):
    toggle_output_button = ObjectProperty(None)
    voltage = NumericProperty()
    current = NumericProperty()

    def start(self, app: ZalpApp):
        app.backend.psu_service.start(
            get_voltage_callback=self.update_voltage_callback,
            get_current_callback=self.update_current_callback,
            update_output_callback=self.update_output_callback
        )

    def stop(self, app: ZalpApp):
        app.backend.psu_service.stop()

    @mainthread
    def update_voltage_callback(self, voltage):
        self.voltage = voltage

    @mainthread
    def update_current_callback(self, current):
        self.current = current

    @mainthread
    def update_output_callback(self, on):
        self.toggle_output_button.state = 'down' if on else 'normal'

    def set_output(self, app, on: bool):
        app.backend.psu_service.set_output(on)


if __name__ == '__main__':
    class MyApp(App):
        def build(self):
            return PsuControlWidget()


    MyApp().run()
