import time

from zalp.application.scenarios import Step, Scenario


class DummyApp:
    def __init__(self):
        self.scenario_pre_flag = False
        self.step_pre_flag = False
        self.step_during_counter = 0
        self.step_post_flag = False
        self.scenario_post_flag = False


STEP_NAME = 'Test step name'
STEP_DESCRIPTION = 'Test step description'
STEP_PERIOD = 0.1  # s
STEP_ITERATIONS = 5


class TestStep(Step):
    name = STEP_NAME
    description = STEP_DESCRIPTION
    period = STEP_PERIOD
    waitable = False

    def pre(self):
        self.app.step_pre_flag = True

    def during(self):
        self.app.step_during_counter += 1

    def is_done(self) -> bool:
        # step will take at least (self.period * STEP_ITERATIONS) seconds
        return time.time() - self.start_time > self.period * (STEP_ITERATIONS - 1)

    def post(self):
        self.app.step_post_flag = True


SCENARIO_NAME = 'Test scenario name'
SCENARIO_DESCRIPTION = 'Test scenario description'


class ExampleScenario(Scenario):
    name = SCENARIO_NAME
    description = SCENARIO_DESCRIPTION
    steps = (
        TestStep,
    )

    def pre(self):
        self.app.scenario_pre_flag = True

    def post(self):
        self.app.scenario_post_flag = True


def test_scenario():
    app = DummyApp()
    scenario = ExampleScenario(app, [], [], [])

    assert scenario.name == SCENARIO_NAME
    assert scenario.description == SCENARIO_DESCRIPTION
    assert scenario.steps[0].name == STEP_NAME
    assert scenario.steps[0].description == STEP_DESCRIPTION
    assert scenario.steps[0].period == STEP_PERIOD

    assert app.scenario_pre_flag is False
    assert app.step_pre_flag is False
    assert app.step_during_counter == 0
    assert app.step_post_flag is False
    assert app.scenario_post_flag is False
    scenario.run()
    assert app.scenario_pre_flag is True
    assert app.step_pre_flag is True
    assert app.step_during_counter == STEP_ITERATIONS
    assert app.step_post_flag is True
    assert app.scenario_post_flag is True
