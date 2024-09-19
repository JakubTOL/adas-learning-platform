import functools
import threading


def run_in_thread(func):
    """
    Wrapper used to schedule the function for running in thread.
    Uses functools.wraps, otherwise it does not work with Kivy WeakMethod
    (so cannot be used with bindable functions).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, name=func.__name__, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper
