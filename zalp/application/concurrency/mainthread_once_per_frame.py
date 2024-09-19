import functools
import threading

from kivy.clock import Clock


def mainthread_once_per_frame(func):
    """
    Wrapper to schedule function execution in Kivy main thread, maximum one time per Kivy frame.

    Implemented behavior is similar to Kivy decorator `mainthread`, but if multiple calls are scheduled in one Kivy
    frame, only the latest one will be carried out in the Kivy thread.
    """
    scheduled_event = None
    lock = threading.Lock()

    @functools.wraps(func)
    def delayed_func(*args, **kwargs):
        def clear_event():
            nonlocal scheduled_event, lock
            with lock:
                scheduled_event = None

        def callback_func(_):
            func(*args, **kwargs)
            clear_event()

        nonlocal scheduled_event, lock
        with lock:
            if scheduled_event is not None:
                Clock.unschedule(scheduled_event)
            scheduled_event = Clock.schedule_once(callback_func, 0)
    return delayed_func
