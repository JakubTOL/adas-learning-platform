import os

from kivy.lang import Builder
from kivy.uix.dropdown import DropDown

__filename = os.path.splitext(os.path.basename(__file__))[0] + '.kv'
__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, __filename))


class ScenarioListDropDown(DropDown):
    pass
