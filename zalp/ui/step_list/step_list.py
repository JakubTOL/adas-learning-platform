import os

from kivy import Config
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from zalp.ui.colors import BRAND_CYAN, BLACK
from zalp.ui.control_widgets.snackbar import ScenarioSnackbar

__directory = os.path.dirname(__file__)
Builder.load_file(os.path.join(__directory, 'step_list.kv'))

ANIMATION_STEP = 1 / float(Config.get('graphics', 'maxfps'))


class StepDisplayWidget(GridLayout):
    step_list_widget = ObjectProperty()
    next_step_button_widget = ObjectProperty()
    step_description_user_input_widget = ObjectProperty()
    scenario_progress_widget = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.steps = None

    def display_step_list(self, steps):
        self.steps = steps
        self.step_list_widget.display_step_list(steps)
        self.scenario_progress_widget.set_in_progress(True)

    @mainthread
    def update_starting_step(self, starting_step):
        self.next_step_button_widget.stop_waiting()
        self.step_list_widget.mark_starting_step(starting_step)
        self.step_description_user_input_widget.update(starting_step)

    @mainthread
    def update_waiting_step(self, waiting_step):
        self.next_step_button_widget.start_waiting()

    # TODO: - scroll to finished step
    #       - mark starting step bold or something?
    @mainthread
    def update_finished_step(self, finished_step):
        self.step_list_widget.mark_finished_step(finished_step)

        if len(self.step_list_widget.layout.children) == finished_step.index:
            self.scenario_progress_widget.set_in_progress(False)
            self.next_step_button_widget.stop_waiting()


class StepWidget(GridLayout):
    step_widget_index = ObjectProperty()
    step_widget_label = ObjectProperty()
    step_widget_checkbox: ObjectProperty()
    name = StringProperty()
    index = NumericProperty()
    active = BooleanProperty(False)

    @classmethod
    def create_step(cls, step):
        return cls(name=step.name, index=step.index)


class StepListWidget(ScrollView):
    layout = ObjectProperty(None)

    def display_step_list(self, steps):
        self.layout.clear_widgets()
        for step in steps:
            self.layout.add_widget(StepWidget.create_step(step))

    def mark_starting_step(self, step):
        starting_step_widget = self._get_widget_from_step(step)
        starting_step_widget.active = True
        self._scroll_to_element(starting_step_widget)

    def mark_finished_step(self, step):
        # TODO: implement waitable
        finished_step_widget = self._get_widget_from_step(step)
        finished_step_widget.active = False
        finished_step_widget.step_widget_checkbox.active = True

    def _get_widget_from_step(self, step):
        return filter(lambda x: step.index == x.index, self.layout.children).__next__()

    def _scroll_to_element(self, element):
        # TODO: for steps in the middle, sometimes it does not scroll exactly to the center
        #       of the element, this calculation might not be correct
        visible_area_height = self.height
        scrollable_area_height = self.layout.height - self.height
        element_top = element.y - self.scroll_y * scrollable_area_height
        element_bottom = element_top + element.height

        if element_top < 0 or element_bottom > visible_area_height:
            # Center the scroll on this element
            element_center_y = (element_top + element_bottom) / 2
            new_scroll_y = (element_center_y - visible_area_height / 2) / scrollable_area_height
            self.scroll_y = max(0, min(1, new_scroll_y))


class NextStepButtonWidget(Button):
    sequence = ObjectProperty()
    duration = 1  # s

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sequence = Animation(background_color=BRAND_CYAN, duration=self.duration, step=ANIMATION_STEP) + \
                        Animation(background_color=BLACK, duration=self.duration, step=ANIMATION_STEP)
        self.sequence.repeat = True

    def start_waiting(self):
        self.disabled = False
        self.start_pulsing()

    def stop_waiting(self):
        self.disabled = True
        self.stop_pulsing()

    def start_pulsing(self):
        self.sequence.start(self)

    def stop_pulsing(self):
        self.sequence.stop(self)

    def request_next_step(self, app):
        app.backend.scenario_runner.next_step()


class ScenarioProgressWidget(BoxLayout):
    is_in_progress = BooleanProperty(True)

    def set_in_progress(self, in_progress):
        self.is_in_progress = in_progress


class StepDescriptionUserInputWidget(GridLayout):
    step_description_widget = ObjectProperty()

    def update(self, step):
        self.clear_widgets()

        step_description_widget = StepDescriptionWidget()
        step_description_widget.update(step)
        self.add_widget(step_description_widget)

        if step.ask_user_input:
            user_input_widget = UserInputWidget(step)
            self.add_widget(user_input_widget)


class StepDescriptionWidget(ScrollView):
    step_description_content = ObjectProperty(None)

    def update(self, step):
        self.step_description_content.text = step.description


class UserInputWidget(GridLayout):
    user_text_input = ObjectProperty()
    checked_ok = BooleanProperty(False)

    def __init__(self, step, **kwargs):
        super().__init__(**kwargs)
        self.step = step

    def check_user_input(self):
        ok = self.step.validate_user_input(self.user_text_input.text)
        if ok:
            text = 'Poprawna odpowiedź!'
            self.checked_ok = True
        else:
            text = 'Niepoprawna odpowiedź!'
        ScenarioSnackbar(text=text).open()
        self.user_text_input.text = ''
        # When correct, disable the check button?


if __name__ == '__main__':
    class MyApp(App):
        def __init__(self):
            super().__init__()

        def build(self):
            root = StepDisplayWidget()
            return root


    # load_dotenv()
    MyApp().run()
