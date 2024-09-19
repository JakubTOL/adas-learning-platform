import os

from kivy.properties import NumericProperty, StringProperty, BoundedNumericProperty
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget

GAUGE_MIN = 0
GAUGE_MAX = 250
COLOR_OK = (1, 1, 1, 1)
COLOR_NOK = (1, 0, 0, 1)

RESOURCES_DIR = os.path.abspath(os.path.join(os.getcwd(), 'resources'))

class Gauge(Widget):
    # load dashboard gauge image
    file_gauge = StringProperty(os.path.join(RESOURCES_DIR, 'pngegg2rem.png'))
    # load needle image
    file_needle = StringProperty(os.path.join(RESOURCES_DIR, 'needle3.png'))
    unit = NumericProperty(1.8)
    # value range for speedmeter widget
    value = BoundedNumericProperty(0, min=GAUGE_MIN, max=GAUGE_MAX, errorvalue=0)
    size_gauge = BoundedNumericProperty(128, min=128, max=256, errorvalue=128)
    size_text = NumericProperty(10)

    def __init__(self, **kwargs):
        super(Gauge, self).__init__(**kwargs)

        self.gauge = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotation=False,
            do_scale=False,
            do_translation=False
        )

        self.img_gauge = Image(source=self.file_gauge, size=(self.size_gauge,
                                                             self.size_gauge))

        self.needle = Scatter(
            size=(self.size_gauge, self.size_gauge),
            do_rotation=False,
            do_scale=False,
            do_translation=False
        )

        self.img_needle = Image(source=self.file_needle, size=(self.size_gauge,
                                                               self.size_gauge))

        # display digitalized speed value as a text
        self.DigitSpeed = Label(font_size=self.size_text, markup=True)

        self.gauge.add_widget(self.img_gauge)
        self.needle.add_widget(self.img_needle)

        self.add_widget(self.gauge)
        self.add_widget(self.needle)
        # add label widget for digitalized speed
        self.add_widget(self.DigitSpeed)

        self.data_valid = True

        self.bind(pos=self.update)
        self.bind(size=self.update)
        self.bind(value=self.turn)

    def update(self, *args):
        self.gauge.pos = self.pos
        self.needle.pos = (self.x, self.y)
        self.needle.center = self.gauge.center
        # update digitalized speed text position
        self.DigitSpeed.center_x = self.gauge.center_x
        # self.DigitSpeed.center_y = self.gauge.center_y + (self.size_gauge / 4)
        self.DigitSpeed.center_y = self.gauge.center_y - (self.size_gauge / 3.8)

    def turn(self, *args):
        """
        Turn needle, 1 degree = 1 unit, 0 degree point start on 50 value.
        """
        self.needle.center_x = self.gauge.center_x
        self.needle.center_y = self.gauge.center_y
        # self.needle.rotation = (50 * self.unit) - (self.value * self.unit)
        # self.needle.rotation = ((125 * self.unit) - (self.value * self.unit)) / 2.5
        self.needle.rotation = ((188 * self.unit) - (self.value * self.unit)) / 2.5
        # update digitalized speed value
        self.DigitSpeed.text = "[b]{0:.0f}[/b]".format(self.value) + "km/h"

    def DataUpdate(self, speed):
        self.data_valid = GAUGE_MIN <= speed <= GAUGE_MAX
        # self.img_gauge.color = COLOR_OK if self.data_valid else COLOR_NOK
        self.img_needle.color = COLOR_OK if self.data_valid else COLOR_NOK
        if int(speed) > 250:
            self.value = 250
            #self.img_needle.color = COLOR_NOK
        else:
            self.value = int(speed)
            #self.img_needle.color = COLOR_OK
