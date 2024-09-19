import os

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout

from zalp.ui import ZalpApp
from zalp.ui.control_widgets.control_widget_base import ControlWidget
from zalp.ui.control_widgets.snackbar import ScenarioSnackbar

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'video_control.kv'))


# TODO: Fix button states (probably do not hardcode, create some state machine in backend implementation
#       and connect it here)
#       Implement stop_player
#       Implement correct path in load_movie


class VideoControlWidget(ControlWidget, GridLayout):
    start_button = ObjectProperty(None)
    pause_button = ObjectProperty(None)
    stop_button = ObjectProperty(None)
    load_button = ObjectProperty(None)
    node = ObjectProperty(None)

    def stop_player(self):
        print("stop video")

        # enable/disable other buttons
        # self.ids.stop_button.disabled = True
        # self.ids.pause_button.disabled = True
        # self.ids.start_button.disabled = True
        # self.ids.load_button.disabled = False

        # TODO: not implemented

    def pause_player(self, app: ZalpApp):
        print("pause video")

        # enable/disable other buttons
        # self.ids.start_button.disabled = False
        # self.ids.pause_button.disabled = True
        # self.ids.stop_button.disabled = False
        # self.ids.load_button.disabled = True

        app.backend.video_player.pause()

    def start_player(self, app: ZalpApp):
        print("start video")

        # enable/disable other buttons
        # self.ids.start_button.disabled = True
        # self.ids.pause_button.disabled = False
        # self.ids.stop_button.disabled = False
        # self.ids.load_button.disabled = True

        app.backend.video_player.play()

    def load_movie(self, app: ZalpApp):
        try:
            app.backend.video_player.load_video(self.node.path)
        except AttributeError:
            ScenarioSnackbar(text='Niewłaściwy wybór wideo').open()

    def on_selected_node(self, _, selected_node):
        self.node = selected_node


if __name__ == '__main__':
    class MyApp(App):
        def build(self):
            return VideoControlWidget()


    MyApp().run()
