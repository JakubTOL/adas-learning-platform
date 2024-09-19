# Workaround for multiprocessing module used in lower layers.
# Without this guard, when new process is spawned, new Kivy instance is run in that process, which
# displays an empty window.
import datetime

from viztracer import VizTracer

if __name__ != '__mp_main__':
    import logging
    import os

    from kivy.config import Config

    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Config.set('kivy', 'exit_on_escape', '0')
    Config.set('graphics', 'maxfps', '25')

    PROFILING = False

    from kivy.core.window import Window
    from kivy.lang import Builder
    from kivy.properties import ObjectProperty
    from kivy.uix.screenmanager import ScreenManager, Screen
    from kivymd.app import MDApp
    from kivy.clock import Clock

    from zalp.application import ZalpBase
    from zalp.application.scenarios import tutorial_scenario_list, challenge_scenario_list

    # TODO: refactor this file to only have main functionality

    logger = logging.getLogger(__name__)


    class ZalpGui(ZalpBase):
        """
        Class integrating GUI functionality with application layer.
        """

        def __init__(self):
            super().__init__()
            pass


    class ZalpApp(MDApp):
        def __init__(self):
            Builder.load_file('zalp\\ui\\gui.kv')

            # DPI fix on Windows
            if os.name == 'nt':
                from ctypes import windll, c_int64

                # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
                windll.user32.SetProcessDpiAwarenessContext(c_int64(-4))

            super().__init__()
            self.backend = ZalpGui()
            self.SM = ScreenManager()

        def build(self):
            # Create the screen manager
            # s = Screen(name='control_widgets')
            # TODO: remove
            # gd = GridLayout(rows=2)
            # gd.add_widget(Button())
            # cwb = ControlWidgetsScrollView()
            # gd.add_widget(cwb)
            # return gd
            # s.add_widget(gd)
            # SM.add_widget(s)
            self.SM.add_widget(StartUpWindow(name='startup_window'))
            self.SM.add_widget(MainWindow(name='main_window'))
            self.SM.add_widget(ScenarioRunnerWindow(name='scenario_runner_window'))
            self.SM.add_widget(ScenarioWindow(name='scenario_window'))
            self.SM.add_widget(ManualModeWindow(name='manual_window'))

            self.icon = os.path.abspath(os.path.join(os.getcwd(), 'resources', '01_logo2.png'))

            return self.SM

        def cleanup(self):
            self.backend.cleanup()


    class StartUpWindow(Screen):
        pass


    def callback1(*args):
        print("Callback triggered!")
        # TODO: Figure out how to return to startup screen
        # ScreenManager.current = StartUpWindow

    # Declare both screens

    class MainWindow(Screen):

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.timer = None

        def on_enter(self, *args):
            # set timer to 5 sec
            self.timer = Clock.schedule_once(callback1, 5)

        def on_leave(self, *args):
            # cancel timer
            self.timer.cancel()
            self.timer = None

        def on_touch_down(self, touch):
            if self.timer is not None:
                self.timer.cancel()
            # reset timer
            self.timer = Clock.schedule_once(callback1, 5)
            return super(MainWindow, self).on_touch_down(touch)

        pass


    # TODO: Refactor so that one ToggleButton must always be pressed
    #       (now both can be depressed - doesn't break the choice, just looks bad)

    # TODO: RelativeLayout + pos_hint
    # class TutorialScenariosWindow(Screen, FloatLayout):
    #     pass


    class ScenarioRunnerWindow(Screen):
        tutorial_btn = ObjectProperty()
        spinner_id = ObjectProperty()
        scenario_name_label = ObjectProperty()
        scenario_description_label = ObjectProperty()

        def __init__(self, **kw):
            super().__init__(**kw)
            self.chosen_scenario = None
            self.scenario_list = None

            self.update_scenario_list()

        def update_scenario_list(self, *args):
            # scenario names as choices
            self.scenario_list = tutorial_scenario_list if self.tutorial_btn.state == 'down' else challenge_scenario_list
            self.spinner_id.values = [sc.name for sc in self.scenario_list]

            # select 1st scenario
            self.spinner_id.text = self.spinner_id.values[0]
            self.choose_scenario()

        def choose_scenario(self, *args):
            self.chosen_scenario = self.scenario_list.get_scenario_by_name(self.spinner_id.text)
            self.update_chosen_scenario()

        def update_chosen_scenario(self, *args):
            self.scenario_name_label.text = self.chosen_scenario.name
            self.scenario_description_label.text = self.chosen_scenario.description

    # class ChallengeScenariosWindow(Screen):
    #     pass
    #
    #
    # class TutorialScenarioWindow(ScenarioWindow):
    #     pass

    class ScenarioWindow(Screen):
        control_widget_parent = ObjectProperty(None)
        rx_control_widget_tabbed_panel = ObjectProperty(None)
        tx_control_widget_tabbed_panel = ObjectProperty(None)
        step_display_widget = ObjectProperty(None)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.scenario = None

        # TODO: clean-up widget references
        # TODO: refactor a lot of below code to starting/cleaning up scenarios
        def prepare_control_widgets(self, app: ZalpApp):
            scenario = app.SM.get_screen('scenario_runner_window').chosen_scenario
            self.scenario = app.backend.scenario_runner.load_scenario(scenario)
            app.backend.scenario_runner.add_pre_step_callback(self.step_display_widget.update_starting_step)
            app.backend.scenario_runner.add_step_waiting_callback(self.step_display_widget.update_waiting_step)
            app.backend.scenario_runner.add_post_step_callback(self.step_display_widget.update_finished_step)

            self.step_display_widget.display_step_list(self.scenario.steps)

            # Reset CAN status before creating widgets, so they do not display anything residual
            app.backend.can_manager.set_default_values()
            app.backend.can_manager.start_rx_handler()
            app.backend.can_manager.start_restbus()
            # Set voltage to default
            app.backend.psu_service.set_voltage()

            self.rx_control_widget_tabbed_panel.add_dummy()
            self.tx_control_widget_tabbed_panel.add_dummy()

            rx_control_widgets = self.rx_control_widget_tabbed_panel.rx_tabbed_panel_content.children[0].layout.children
            for widget in rx_control_widgets:
                widget.start(app)

            self.rx_control_widget_tabbed_panel.can_traffic_analyzer_widget_content.children[0].layout.children[
                0].start(
                app)

            tx_control_widgets = self.tx_control_widget_tabbed_panel.tx_tabbed_panel_content.children[0].layout.children
            for widget in tx_control_widgets:
                widget.start(app)
            # DiagnosticWidget start
            self.tx_control_widget_tabbed_panel.diagnostic_tabbed_panel_content.children[0].start(app)
            logger.info('ScenarioWindow: ControlWidgets created')

            app.backend.can_manager.set_initialization_values()
            app.backend.scenario_runner.run_scenario()

        def clear_control_widgets(self, app: ZalpApp):
            app.backend.scenario_runner.cancel()
            app.backend.scenario_runner.clear_pre_step_callbacks()
            app.backend.scenario_runner.clear_post_step_callbacks()

            app.backend.can_manager.stop_restbus()
            app.backend.can_manager.stop_rx_handler()
            app.backend.can_manager.can1.set_tester_present(False)
            app.backend.psu_service.set_output(False)

            rx_control_widgets = self.rx_control_widget_tabbed_panel.rx_tabbed_panel_content.children[0].layout.children
            for widget in rx_control_widgets:
                widget.stop(app)

            self.rx_control_widget_tabbed_panel.can_traffic_analyzer_widget_content.children[0].layout.children[0].stop(
                app)

            tx_control_widgets = self.tx_control_widget_tabbed_panel.tx_tabbed_panel_content.children[0].layout.children
            for widget in tx_control_widgets:
                widget.stop(app)

            # DiagnosticWidget start
            self.tx_control_widget_tabbed_panel.diagnostic_tabbed_panel_content.children[0].stop(app)

            self.rx_control_widget_tabbed_panel.rx_tabbed_panel_content.clear_widgets()
            self.rx_control_widget_tabbed_panel.can_traffic_analyzer_widget_content.clear_widgets()
            self.tx_control_widget_tabbed_panel.tx_tabbed_panel_content.clear_widgets()
            self.tx_control_widget_tabbed_panel.diagnostic_tabbed_panel_content.clear_widgets()
            self.tx_control_widget_tabbed_panel.video_tabbed_panel_content.clear_widgets()

            app.backend.video_player.load_video()

            logger.info('ScenarioWindow: ControlWidgets destroyed')


    class ManualModeWindow(Screen):
        pass


    if __name__ == '__main__':
        try:
            if PROFILING:
                tracer = VizTracer()
                tracer.start()
                tracer.enable_thread_tracing()
                # profile = Profile()
                # profile.enable()
            # move to main dir
            os.chdir(r'..\..')
            # Enable escape window by "ESC" [1], disable [0]
            app = ZalpApp()
            # TODO: refactor window size
            # fullscreen size window. Press "ESC' key to escape.
            Window.fullscreen = 'auto'
            # manual window size set
            Window.size = (1280, 720)
            app.run()
            # app.cleanup()
        except KeyboardInterrupt:
            pass
        finally:
            if PROFILING:
                tracer.stop()
                filename = f'profile_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.json'
                tracer.save(filename)
                # profile.disable()
                # Stats(profile).sort_stats('tottime').print_stats(10)
                # filename = f'profile_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.prof'
                # profile.dump_stats(filename)
            app.cleanup()
            print("Shutdown requested. Clean-up pending")
            os._exit(300)
