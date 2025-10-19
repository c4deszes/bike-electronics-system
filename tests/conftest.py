from bike_testframework.ip_chamber.chamber import IPChamberController
from bike_testframework.devices.gpp_x323 import GppPsu
import time
from pyvisa import ResourceManager
import pytest
from line_protocol.network import load_network, Network
from line_protocol.protocol import LineMaster, LineSerialTransport

@pytest.fixture
def chamber():
    chamber = IPChamberController(port='COM15')
    chamber.connect()

    # Setup
    chamber.set_steps_per_rotation('U', 1600)
    chamber.set_steps_per_rotation('V', 2000)
    chamber.set_steps_per_rotation('H', 2000)
    #chamber.set_limits('U', -180, 180)
    #chamber.set_limits('V', -90, 180)
    #chamber.set_limits('H', -360, 360)

    yield chamber
    chamber.disconnect()

@pytest.fixture
def network():
    network = load_network('network.json')
    yield network

@pytest.fixture
def line_transport(network):
    with LineSerialTransport('COM9', baudrate=network.baudrate, one_wire=True) as transport:
        yield transport

@pytest.fixture
def line_master(line_transport, network):
    with LineMaster(line_transport, network) as master:
        yield master

@pytest.fixture
def resource_manager():
    rm = ResourceManager()
    yield rm
    rm.close()

@pytest.fixture
def psu(resource_manager):
    with GppPsu(resource_manager, 'ASRL18::INSTR') as psu:  # Update port as needed
        psu.info()
        yield psu

@pytest.fixture
def chamber_channel(psu):
    yield psu.get_channel(0)

@pytest.fixture
def dut_channel(psu):
    yield psu.get_channel(1)
