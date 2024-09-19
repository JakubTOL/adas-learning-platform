import logging
from abc import ABC

from .scenario_event_handler import ScenarioEventHandler

logger = logging.getLogger(__name__)

DEFAULT_SCENARIO_NAME = 'Default scenario name'
DEFAULT_SCENARIO_DESCRIPTION = 'Default scenario description'


class Scenario(ABC):
    """
    Base class defining scenario to be run.

    Scenario is a process defining:
    - what needs to happen before the run
    - steps of a scenario
        - what happens automatically at the beginning of the step
        - conditions to check to allow moving to next step
    - what needs to happen after the run
    """
    name = DEFAULT_SCENARIO_NAME
    description = DEFAULT_SCENARIO_DESCRIPTION
    steps = tuple()

    def __init__(self, app, pre_step_callbacks, step_waiting_callbacks, post_step_callbacks):
        """
        Create Scenario instance.
        :param app: ZalpBase instance, used to allow Scenario to communicate with the application
        """
        self.app = app
        self.pre_step_callbacks = pre_step_callbacks
        self.step_waiting_callbacks = step_waiting_callbacks
        self.post_step_callbacks = post_step_callbacks
        self.event_handler = ScenarioEventHandler()

        if self.name == DEFAULT_SCENARIO_NAME:
            logger.warning(f'Creating Scenario with default name', stack_info=True)

        if self.description == DEFAULT_SCENARIO_DESCRIPTION:
            logger.warning(f'Creating Scenario with default description', stack_info=True)

        # create instance of all Steps
        self.steps = tuple(step(app=app,
                                index=index,
                                event_handler=self.event_handler,
                                step_waiting_callbacks=self.step_waiting_callbacks)
                           for index, step in enumerate(self.__class__.steps, start=1))

        if not self.steps:
            logger.warning(f'Scenario: {self.name} has no steps defined', stack_info=True)

    def _pre_parent(self):
        """
        Function which is run at the beginning of every scenario.
        Probably reset all CAN signal values, enable camera voltage etc.
        NOT to be subclassed in concrete Scenario implementations.
        """
        pass

    def pre(self):
        """
        Function which is run at the beginning of a scenario.

        This function should be subclassed in concrete scenario to add scenario-specific
        initialization routine.
        """
        pass

    def run(self):
        """
        Function which is run during the scenario.
        This will iterate through steps, running them one by one.
        """
        self._pre_parent()
        self.pre()

        # TODO: Check if below error handling is fine.
        #       If any exception will be raised during scenario execution,
        #       it will be reraised (which will cause thread's death), but
        #       post and _post_parent call will be executed to allow scenario to clean-up any
        #       used resources.
        try:
            for step in self.steps:
                for callback in self.pre_step_callbacks:
                    callback(step)

                cancelled = step.run()
                if cancelled:
                    logger.warning(f'Scenario: Scenario "{self.name}" cancelled during Step "{step.name}"')
                    break

                for callback in self.post_step_callbacks:
                    callback(step)
        finally:
            self.post()
            self._post_parent()

    def post(self):
        """
        Function which is run at the end of a scenario.

        This function can be subclassed in concrete scenario to add scenario-specific
        clean-up routine.
        """
        pass

    def _post_parent(self):
        """
        Function which is run at the end of every scenario.

        NOT to be subclassed in concrete Scenario implementations.
        """
        pass

    def cancel(self):
        """
        Request cancellation of a scenario.
        """
        self.event_handler.cancel_scenario()

    def next_step(self):
        """
        Request next step of a scenario.
        Only applicable if step is waitable and is currently waiting.
        """
        self.event_handler.next_step()
