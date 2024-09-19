import pytest

from zalp.domain.psu.utils import voltage_format


@pytest.mark.parametrize(
    'voltage, formatted',
    [
        (0, '0'),
        (5, '5'),
        (12, '12'),
        (15.2, '15.2'),
        (14.32, '14.32'),
        (6.123, '6.12'),
        (6.128, '6.13'),
        (11.123, '11.12'),
        (11.128, '11.13')
    ]
)
def test_voltage_format(voltage, formatted):
    assert voltage_format(voltage) == formatted
