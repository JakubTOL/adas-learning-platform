import time

from zalp.application.scenarios import Step, Scenario


class Step1(Step):
    name = 'Camera init'
    description = 'Camera is being initialized'

    def pre(self):
        print('Step1 pre another')

    def is_done(self) -> bool:
        return time.time() - self.start_time > 5

    def post(self):
        print('Step1 post another')


class AnotherExampleScenario(Scenario):
    name = 'Another example scenario'
    description = 'This scenario does some more stuff'
    steps = (
        Step1,
        Step1
    )
