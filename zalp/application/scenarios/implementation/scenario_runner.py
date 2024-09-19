import logging
from typing import Type

from zalp.application.concurrency import run_in_thread
from . import Scenario

logger = logging.getLogger(__name__)


class ScenarioRunner:
    """
    High-level class implementing execution of Scenarios.
    """

    def __init__(self, app):
        self.app = app
        self.scenario = None
        self.scenario_running = False
        self.pre_step_callbacks = []
        self.step_waiting_callbacks = []
        self.post_step_callbacks = []

    def load_scenario(self, scenario: Type[Scenario]) -> Scenario:
        self.scenario = scenario(app=self.app,
                                 pre_step_callbacks=self.pre_step_callbacks,
                                 step_waiting_callbacks=self.step_waiting_callbacks,
                                 post_step_callbacks=self.post_step_callbacks)
        logger.info(f'ScenarioRunner: Prepared Scenario "{self.scenario.name}"')
        return self.scenario

    # TODO: possibility for multi-thread access for these lists - lock them
    def add_pre_step_callback(self, callback):
        if self.scenario is None:
            raise ValueError('No scenario loaded')
        self.pre_step_callbacks.append(callback)

    def clear_pre_step_callbacks(self):
        self.pre_step_callbacks.clear()

    def add_step_waiting_callback(self, callback):
        if self.scenario is None:
            raise ValueError('No scenario loaded')
        self.step_waiting_callbacks.append(callback)

    def clear_step_waiting_callbacks(self):
        self.step_waiting_callbacks.clear()

    def add_post_step_callback(self, callback):
        if self.scenario is None:
            raise ValueError('No scenario loaded')
        self.post_step_callbacks.append(callback)

    def clear_post_step_callbacks(self):
        self.post_step_callbacks.clear()

    @run_in_thread
    def run_scenario(self):
        """
        Runs prepared scenario in a new thread.

        :return: Thread of running scenario
        """
        try:
            logger.info(f'ScenarioRunner: Starting execution of Scenario "{self.scenario.name}"')
            self.scenario_running = True
            self.scenario.run()
            logger.info(f'ScenarioRunner: Execution of Scenario "{self.scenario.name}" finished')
        finally:
            self.scenario = None
            self.scenario_running = False

    def is_scenario_running(self):
        return self.scenario_running

    def cancel(self):
        if not self.scenario:
            return
        logger.info(f'ScenarioRunner: Cancelling execution of Scenario "{self.scenario.name}"')
        self.scenario.cancel()

    def next_step(self):
        if not self.scenario:
            return
        self.scenario.next_step()
