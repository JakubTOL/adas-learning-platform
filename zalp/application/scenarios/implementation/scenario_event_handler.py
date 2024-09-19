from threading import Event


class ScenarioEventHandler:

    def __init__(self):
        self._cancel_event = Event()
        self._next_step_event = Event()

        self._stop_waiting_event = Event()

    def clear(self):
        self._cancel_event.clear()
        self._next_step_event.clear()
        self._stop_waiting_event.clear()

    def cancel_scenario(self):
        self._cancel_event.set()
        self._stop_waiting_event.set()

    def is_scenario_cancelled(self):
        return self._cancel_event.is_set()

    def next_step(self):
        self._next_step_event.set()
        self._stop_waiting_event.set()

    def is_next_step(self):
        return self._next_step_event.is_set()

    def force_stop_wait(self):
        self._stop_waiting_event.set()

    def wait(self, timeout):
        self._stop_waiting_event.wait(timeout)
