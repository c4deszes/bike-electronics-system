from line_protocol.protocol.master import LineMaster
from line_protocol.protocol.simulation import SimulatedPeripheral
from line_protocol.network import load_network, Network
from line_protocol.monitor.traffic import TrafficLogger
from line_protocol.protocol.transport import LineSerialTransport
from line_uds.uds_tool import UdsTool, load_profile
from line_uds.simulation import SimulatedUdsExtension

import logging
import threading
import time
import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

# Peripherals
from body_computer import BodyComputerControlPanel
from rear_light import RearLightStatusPanel
from rotor_sensor import RotorSensorStatusPanel, RotorSensorSpeedPanel

# Utilities
from views.schedule_control import ScheduleControl
from line_uds.ui.node_editor import UdsNodesEditor

class SimulationContext:
    def __init__(self, network: Network):
        self.network = network

    def setup(self):

        self.rotor_sensor_node = self.network.get_node("RotorSensor")
        self.rotor_sensor_uds_profile = load_profile(os.path.join(os.path.dirname(__file__), '..', 'uds', 'rotor_sensor.json')) 
        #self.rotor_sensor_uds_extension = SimulatedUdsExtension(self.rotor_sensor_uds_profile)

        self.rear_light_node = self.network.get_node("RearLight")
        self.rear_light_uds_profile = load_profile(os.path.join(os.path.dirname(__file__), '..', 'uds', 'rear_light.json'))
        #self.rear_light_uds_extension = SimulatedUdsExtension(self.rear_light_uds_profile)

        self.front_light_node = self.network.get_node("FrontLight")
        self.front_light_uds_profile = load_profile(os.path.join(os.path.dirname(__file__), '..', 'uds', 'front_light.json'))
        #self.front_light_uds_extension = SimulatedUdsExtension(self.front_light_uds_profile)

        self.body_computer = SimulatedPeripheral(self.network.get_node("BodyComputer"))

        #self.rotor_sensor = SimulatedPeripheral(self.rotor_sensor_node)
        #self.rotor_sensor.requests.SpeedStatus.SpeedState = 'Ok'
        #self.rotor_sensor.add_extension(self.rotor_sensor_uds_extension)

        #self.rear_light = SimulatedPeripheral(self.rear_light_node)
        #self.rear_light.add_extension(self.rear_light_uds_extension)

        #self.front_light = SimulatedPeripheral(self.front_light_node)
        #self.front_light.add_extension(self.front_light_uds_extension)

class BusThread(threading.Thread):
    def __init__(self, context: SimulationContext):
        super().__init__()
        self.context = context
        self.running = True
        self.transport = LineSerialTransport('/dev/ttyFTDI_B', self.context.network.baudrate)
        self.master = LineMaster(transport=self.transport, network=self.context.network)
        self.uds_tool = UdsTool(self.master)
        self.uds_tool.load_profile(self.context.rear_light_node, self.context.rear_light_uds_profile)
        self.uds_tool.load_profile(self.context.front_light_node, self.context.front_light_uds_profile)
        self.uds_tool.load_profile(self.context.rotor_sensor_node, self.context.rotor_sensor_uds_profile)
    def run(self):
        with self.transport:
            with self.master:
                self.master.virtual_bus.add(self.context.body_computer)
                #self.master.virtual_bus.add(self.context.rotor_sensor)
                #self.master.virtual_bus.add(self.context.rear_light)
                #self.master.virtual_bus.add(self.context.front_light)
                with self.uds_tool:

                    while self.running:
                        time.sleep(0.1)

                self.master.disable_schedule()

    def stop(self):
        self.running = False
        #self.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication([])
    app.setApplicationName("Device configuration")
    window = QWidget()

    main_layout = QGridLayout()

    simulation_context = SimulationContext(load_network(os.path.join(os.path.dirname(__file__), '..', 'network.json')))
    simulation_context.setup()
    
    bus_thread = BusThread(simulation_context)

    def closeEvent(event):
        bus_thread.stop()
        event.accept()

    # schedule_control = ScheduleControl(bus_thread.master, simulation_context.network.schedules)
    # body_computer_control_panel = BodyComputerControlPanel(simulation_context.body_computer)
    # rotor_sensor_status_panel = RotorSensorStatusPanel(bus_thread.master, simulation_context.network)

    uds_nodes_editor = UdsNodesEditor({
        simulation_context.rotor_sensor_node: simulation_context.rotor_sensor_uds_profile,
        simulation_context.rear_light_node: simulation_context.rear_light_uds_profile,
        simulation_context.front_light_node: simulation_context.front_light_uds_profile
    }, tool=bus_thread.uds_tool)

    # main_layout.addWidget(schedule_control, 0, 0, 1, 2)
    # main_layout.addWidget(body_computer_control_panel, 1, 0, 1, 2)
    # main_layout.addWidget(rotor_sensor_status_panel, 2, 0, 1, 2)
    main_layout.addWidget(uds_nodes_editor, 0, 0, 1, 1)

    bus_thread.start()

    window.closeEvent = closeEvent
    window.setLayout(main_layout)
    window.show()
    app.exec()