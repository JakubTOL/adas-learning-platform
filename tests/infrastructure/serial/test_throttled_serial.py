from zalp.infrastructure.serial.throttled_serial import *


def test_throttled_serial():
    serial = ThrottledSerial()
    dummy_write(serial)

    start_time = time.time()
    dummy_write(serial)
    end_time = time.time()

    duration = end_time - start_time
    assert duration > THROTTLE_TIMER_THRESHOLD


def dummy_write(s):
    try:
        s.write('asd'.encode())
    except serial.serialutil.PortNotOpenError:
        pass
