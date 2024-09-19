import os
import re

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from zalp.ui import ZalpApp

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'control_widget_base.kv'))


class ControlWidget(Widget):
    """
    Class used to implement a widget which is connecting to the application layer
    at the start of the scenario.
    """

    def start(self, app: ZalpApp):
        """
        Connect ControlWidget to the application layer.

        To be overriden in concrete ControlWidget implementations.
        :param app: ZalpBase instance
        """
        pass

    def stop(self, app: ZalpApp):
        """
        Stop connection of ControlWidget to the application layer.
        To be overriden in concrete ControlWidget implementations.

        :param app: ZalpBase instance
        """
        pass


class HorizontalControlWidget(ControlWidget, BoxLayout):
    """
    Class used to implement horizontal control widgets for RX and TX tabs.
    """
    layout = ObjectProperty()
    title = ObjectProperty()

    def __init__(self, **kwargs):
        """
        Some trickery is performed here to:
          - allow subclasses to add widget easily in .kv files
          - separate title and content to allow for different padding etc. in both
        """
        # Create the layout instance for content
        layout = HorizontalControlWidgetLayout()
        self.layout = layout

        # Save original reference to add_widget. Replace it with local implementation.
        # This implementation will redirect all calls to the content layout.
        add_widget_parent = self.add_widget
        self.add_widget = self.add_widget_to_layout

        # Subclasses widgets are created and added to the layout in this call.
        super().__init__(**kwargs)

        # Create the title label
        label = HorizontalControlWidgetLabel(
            text=self.title
        )

        # Finally, add both title label and content layout to the actual parent widget.
        add_widget_parent(label)
        add_widget_parent(layout)

    def add_widget_to_layout(self, widget, *args, **kwargs):
        return self.layout.add_widget(widget, *args, **kwargs)


class HorizontalControlWidgetLayout(BoxLayout):
    pass


class HorizontalControlWidgetLabel(Label):
    pass


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)
