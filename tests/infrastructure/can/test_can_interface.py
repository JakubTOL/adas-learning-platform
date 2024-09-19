import pytest

from zalp.infrastructure.canbus.can_interface import CanInterface
from zalp.infrastructure.canbus.exceptions import CanInterfaceNotImplementedError

name = 'MYCAN'
ENV_VAR_INTERFACE = f'CAN_INTERFACE_{name}'
ENV_VAR_CHANNEL = f'CAN_CHANNEL_{name}'
ENV_VAR_BITRATE = f'CAN_BITRATE_{name}'

INTERFACE = 'vector'
CHANNEL = '0'
BITRATE = '500000'


@pytest.fixture
def can_env_setup(monkeypatch):
    monkeypatch.setenv(ENV_VAR_INTERFACE, INTERFACE)
    monkeypatch.setenv(ENV_VAR_CHANNEL, CHANNEL)
    monkeypatch.setenv(ENV_VAR_BITRATE, BITRATE)


def test_can_interface_init_incorrect_interface(monkeypatch, can_env_setup):
    monkeypatch.delenv(ENV_VAR_INTERFACE)
    with pytest.raises(CanInterfaceNotImplementedError):
        c = CanInterface(name=name)


def test_can_interface_init_incorrect_channel(monkeypatch, can_env_setup):
    monkeypatch.delenv(ENV_VAR_CHANNEL)
    with pytest.raises(CanInterfaceNotImplementedError):
        c = CanInterface(name=name)

# do not try to initialize interface in unit tests
# def test_can_interface_init_correct(can_env_setup):
#     try:
#         c = CanInterface(name=name)
#     # interface might or might not be connected, either way env setting is correct
#     except CanInterfaceInitializationError:
#         pass
