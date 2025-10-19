from bike_testframework.ip_chamber.chamber import IPChamberController
import time
from line_protocol.protocol.simulation import SimulatedPeripheral

import pytest

@pytest.fixture
def body_computer(network):
    return SimulatedPeripheral(network.get_node("BodyComputer"))

@pytest.fixture
def master_setup(line_master, body_computer):
    line_master.virtual_bus.add(body_computer)

    line_master.enable_schedule('FrontLightSchedule')
    yield
    line_master.disable_schedule()


@pytest.fixture
def dut_setup(dut_channel):
    # Turn on Power for DUT
    dut_channel.set_voltage(12)
    dut_channel.set_current(1.0)
    dut_channel.enable()
    time.sleep(2)

    yield

    # Turn off Power for DUT
    time.sleep(1)
    dut_channel.disable()

@pytest.fixture
def chamber_setup(chamber, chamber_channel):

    # Turn on Power for chamber
    chamber_channel.set_voltage(12)
    chamber_channel.set_current(1.5)
    chamber_channel.enable()
    time.sleep(5)

    # Setup before each test
    chamber.enable_steppers('UVH')
    chamber.zero_axes()
    chamber.move_to(0, 0, 0, feedrate=5, mode='TIME')

    # Enable pumps
    chamber.enable_pumps()
    time.sleep(1)

    yield chamber

    # Teardown after each test
    time.sleep(1)
    chamber.disable_pumps()
    chamber.move_to(u=0, v=0, h=0, feedrate=1, mode='SPEED')
    chamber.disable_steppers('UVH')

    # Turn off Power for chamber
    time.sleep(1)
    chamber_channel.disable()

def test_frontlight(master_setup, dut_setup, chamber_setup, body_computer):
    body_computer.requests.LightSynchronization.TargetBrightness = 50
    body_computer.requests.LightSynchronization.LightMode = 'Adaptive'
    body_computer.requests.FrontLightSetting.Behavior = 'Solid'

    time.sleep(5)

    u_position = 0
    u_dir = 1

    for x in range(100):
        chamber_setup.move_to(h=+60, feedrate=1.4, mode='TIME')
        time.sleep(0.5)
        chamber_setup.move_to(h=-60, feedrate=1.4, mode='TIME')
        time.sleep(0.5)

        u_position += 5 * u_dir
        if abs(u_position) >= 45:
            u_dir *= -1
        chamber_setup.move_to(u=u_position, feedrate=1.5, mode='TIME')

    body_computer.requests.LightSynchronization.TargetBrightness = 0
    body_computer.requests.LightSynchronization.LightMode = 'Adaptive'
    body_computer.requests.FrontLightSetting.Behavior = 'Solid'

    time.sleep(5)
