import sys


def test_python_version():
    assert sys.version_info[0] == 3
    assert sys.version_info[1] == 11
