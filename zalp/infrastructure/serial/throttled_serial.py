import time

import serial

THROTTLE_TIMER_THRESHOLD = 0.05  # s


class ThrottledSerial(serial.Serial):
    def __init__(self, *args, **kwargs):
        self._last_write_timestamp = time.time()
        super().__init__(*args, **kwargs)

    def write(self, data):
        try:
            # if last write ended before THROTTLE_TIMER_THRESHOLD, wait until this timer expires
            elapsed = time.time() - self._last_write_timestamp
            if elapsed < THROTTLE_TIMER_THRESHOLD:
                time.sleep(THROTTLE_TIMER_THRESHOLD - elapsed)
            super().write(data)

        # if SerialException happened, make sure to update the timer anyway
        except serial.serialutil.SerialException:
            raise
        finally:
            self._last_write_timestamp = time.time()
