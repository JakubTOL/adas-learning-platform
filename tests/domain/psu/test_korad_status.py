import pytest

from zalp.domain.psu import Korad


@pytest.mark.parametrize(
    'prop, value',
    [
        ('beep', Korad.Status.BEEP),
        ('lock', Korad.Status.LOCK),
        ('output', Korad.Status.OUTPUT),
    ]
)
def test_properties(prop, value):
    k = Korad.Status(value)
    assert getattr(k, prop)
    k = Korad.Status(0)
    assert not getattr(k, prop)


def test_from_char():
    k = Korad.Status.from_char('Q')
    assert k == Korad.Status(Korad.Status.CH1_STATE | Korad.Status.BEEP | Korad.Status.OUTPUT)
