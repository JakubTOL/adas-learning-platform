import os

from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeView

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'common_widgets.kv'))


class AdaptableHeightGridLayout(GridLayout):
    pass


class AdaptableHeightTextInput(TextInput):
    pass


class AdaptableHeightTreeView(TreeView):
    pass


class AdaptableHeightButton(Button):
    pass


class AdaptableHeightLabel(Label):
    pass
