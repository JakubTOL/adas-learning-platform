from contextlib import nullcontext

import pytest

from zalp.domain.psu.exceptions import KoradIncorrectResponseException
from zalp.domain.psu.korad import Korad


class MockKoradSerialInterface:
    def open(self):
        pass

    def close(self):
        pass

    def read_until(self, *args, **kwargs):
        pass

    def write(self, *args, **kwargs):
        pass


@pytest.fixture
def korad():
    return Korad(interface=MockKoradSerialInterface())


@pytest.mark.parametrize(
    'voltage', [0, 0.2, 1, 3.21, 12, 12.6, 13.42]
)
def test_get_voltage(monkeypatch, korad, voltage):
    def mock_read(*args, **kwargs):
        return f'{voltage:05.2f}'.encode()

    monkeypatch.setattr(korad.interface, "read_until", mock_read)
    voltage_read = korad.get_voltage()

    assert voltage_read == voltage


@pytest.mark.parametrize(
    'voltage, response',
    [(0, 'VSET1:0'), (0.2, 'VSET1:0.2'), (1, 'VSET1:1'), (3.21, 'VSET1:3.21'), (12, 'VSET1:12'), (12.6, 'VSET1:12.6'),
     (13.42, 'VSET1:13.42')],
)
def test_set_voltage(monkeypatch, korad, voltage, response):
    def mock_write(data):
        assert data == response.encode()

    monkeypatch.setattr(korad.interface, "write", mock_write)
    korad.set_voltage(voltage)


@pytest.mark.parametrize(
    'response, result', [('KORADV13.0PSU', nullcontext()),
                         ('', pytest.raises(KoradIncorrectResponseException)),
                         ('Lorem.Ipsum', pytest.raises(KoradIncorrectResponseException))]
)
def test_selftest(monkeypatch, korad, response, result):
    def mock_read(*args, **kwargs):
        return response.encode()

    def mock_write(data):
        assert data == '*IDN?'.encode()

    monkeypatch.setattr(korad.interface, "write", mock_write)
    monkeypatch.setattr(korad.interface, "read_until", mock_read)

    with result:
        korad.selftest()
