import logging
import time
from abc import ABC

from .scenario_event_handler import ScenarioEventHandler

logger = logging.getLogger(__name__)

DEFAULT_STEP_NAME = 'Default step name'
DEFAULT_STEP_DESCRIPTION = 'Default step description'


class Step(ABC):
    """
    Base class of a scenario step.

    Defines:
    - what happens before a step
    - what happens during each step iteration (every period)
    - how to check when step is done
    - what happens after a step
    """
    name = DEFAULT_STEP_NAME
    description = DEFAULT_STEP_DESCRIPTION

    # default values
    period = 0.5  # s
    ask_user_input = False
    minimum_time = 1  # s
    # user_input_choices = []

    waitable = True

    def __init__(self,
                 app,
                 index,
                 event_handler: ScenarioEventHandler,
                 step_waiting_callbacks):
        """
        Create Step instance.
        :param app: ZalpBase instance, used to allow Scenario to communicate with the application
        :param index: index of a step in the scenario
        :param event_handler: ScenarioEventHandler instance, can be shared between steps
        """
        self.app = app
        self.start_time = 0
        self.index = index
        self.event_handler = event_handler
        self.step_waiting_callbacks = step_waiting_callbacks

        if self.name == DEFAULT_STEP_NAME:
            logger.warning(f'Creating Step with default name', stack_info=True)

        if self.description == DEFAULT_STEP_DESCRIPTION:
            logger.warning(f'Creating Step with default description', stack_info=True)

        # Variable 'done' is an optional flag that needs to be set to pass the step.
        # It's used when user input is requested.
        self.done = False if self.ask_user_input else True

    def run(self) -> bool:
        """
        Run Step implementation.
        :return: True if Step execution was cancelled, False otherwise
        """
        cancelled = False

        self._pre_parent()
        self.pre()

        # TODO: Check if this error handling is enough.
        #       If any exception happens during execution of main loop,
        #       it will be reraised, but post and _post_parent calls will still be executed
        #       to allow step to clean-up any resources it used.
        try:
            while True:
                self.during()
                if self.is_done():
                    break

                # TODO: refactor hardcoded wait into calculating how much time elapsed
                #       from start of current iteration and wait only the remaining time.
                #       Useful if step iteration takes more than insignificant amount of execution time
                #       (but ideally steps should not do it).
                self.event_handler.wait(self.period)

                if self.event_handler.is_scenario_cancelled():
                    cancelled = True
                    break

            # If step is waitable, send step waiting callbacks.
            # Block until scenario is cancelled or request of "next" step if received.
            if self.waitable:
                for callback in self.step_waiting_callbacks:
                    callback(self)
                self.event_handler.wait(None)

                if self.event_handler.is_scenario_cancelled():
                    cancelled = True
                elif self.event_handler.is_next_step():
                    pass
                else:
                    raise RuntimeError
        finally:
            self.post()
            self._post_parent()

        return cancelled

    def _pre_parent(self):
        """
        Function executed before every Step.
        NOT to be subclassed in concrete Step implementations.
        """
        self.start_time = time.time()

    def pre(self):
        """
        Function executed before a Step.
        To be subclassed in concrete Step implementation.
        """
        pass

    def during(self):
        """
        Function executed every iteration of a Step (every period).
        To be subclassed in concrete Step implementation.
        """
        pass

    def is_done(self) -> bool:
        """
        Function executed every iteration of a Step (every period)
        to check whether the Step should be finished.

        Should be subclassed in concrete Step implementation.
        :return: True if Step should be finished, False otherwise
        """
        # TODO: experimental: if step is instant, hold it for a minimum time (default - 1 second) at least
        #       to account for double clicks in UI
        return self.done and time.time() - self.start_time > self.minimum_time
        # return self.done

    def validate_user_input(self, user_input):
        """
        Check if user provided correct input and set done criteria accordingly. Called by UX code.

        This method SHOULD NOT be overriden in concrete Steps.
        Instead, steps should override `is_user_input_correct` method.
        :param user_input:
        :return:
        """
        ok = self.is_user_input_correct(user_input)
        if ok:
            self.done = True
        return ok

    def is_user_input_correct(self, user_input):
        """
        Check if user provided correct.

        This method should be overriden in concrete steps.
        Default implementation considers every input as correct.
        :param user_input: value provided by user to be checked
        :return: True if user input is correct, False otherwise
        """
        return True

    def post(self):
        """
        Function executed after a Step.
        To be subclassed in concrete Step implementation.
        """
        pass

    def _post_parent(self):
        """
        Function executed after a Step.
        NOT to be subclassed in concrete Step implementation.
        """
        self.event_handler.clear()

    def has_elapsed_time(self, time_to_check: float) -> bool:
        """
        Check if time_to_check has elapsed since start of the step.
        :param time_to_check: time to check, in seconds
        :return: True if elapsed, False otherwise
        """
        return time.time() - self.start_time > time_to_check

    def force_next_iteration(self):
        """
        Force the next step iteration immediately.
        To be used in e.g. user callback.
        `during()` and `is_done()` will be called, so step end condition will be checked.

        Note: calling this function when step is waitable and is currently waiting
        will raise a RuntimeError. To request a next step, use `Scenario.next_step()`.
        """
        # TODO: discuss whether this is appropriate. Would some `during()` implementation
        #       benefit from breaking the strict time schedule when calling this function
        #       (every period), or should this not be allowed?
        raise NotImplementedError
        # self.event_handler.force_stop_wait()
