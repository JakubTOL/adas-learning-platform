import time

from zalp.application.scenarios import Step, Scenario


class Step1(Step):
    name = 'Kamera init'
    description = 'Kamera w trakcie inicjalizacji'
    waitable = True

    def pre(self):
        print('Step1 pre')

    def during(self):
        print('Step1 during')

    def is_done(self) -> bool:
        return time.time() - self.start_time > 5

    def post(self):
        print('Step1 post')


class ExampleScenario(Scenario):
    name = 'Przykładowy scenariusz'
    description = 'W tym scenariuszu zrobisz to i tamto'
    steps = (
        Step1,
        Step1
    )
