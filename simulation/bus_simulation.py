from line_protocol.protocol.master import LineMaster
from line_protocol.protocol.simulation import SimulatedPeripheral
from line_protocol.network import load_network, Network
from line_protocol.monitor.traffic import TrafficLogger
from line_protocol.protocol.transport import LineSerialTransport
import logging
import threading
import time
import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

# Peripherals
from body_computer import BodyComputerSimulation
from rear_light import RearLightSimulationPanel, RearLightSimulation, RearLightStatusPanel
from rotor_sensor import RotorSensorSimulation
from front_light import FrontLightSimulation, FrontLightSimulationPanel

# Utilities
from util.schedule_control import ScheduleControl
from util.diag_view import DiagnosticInfoView

class SimulationContext:
    def __init__(self, network: Network):
        self.network = network

    def setup(self):
        self.body_computer = BodyComputerSimulation(self.network.get_node("BodyComputer"))

        self.rotor_sensor = RotorSensorSimulation(self.network.get_node("RotorSensor"))
        self.rotor_sensor.software_version = '1.2.3'
        self.rotor_sensor.serial_number = 0x12345678

        self.rear_light = RearLightSimulation(self.network.get_node("RearLight"))
        self.rear_light.software_version = '1.0.0'
        self.rear_light.serial_number = 0x87654321

        self.front_light = FrontLightSimulation(self.network.get_node("FrontLight"))
        self.front_light.software_version = '1.0.0'
        self.front_light.serial_number = 0x11223344

class SimulationThread(threading.Thread):
    def __init__(self, context: SimulationContext):
        super().__init__()
        self.context = context
        self.running = False

    def run(self):
        self.running = True
        self.context.body_computer.start()
        #self.context.rotor_sensor.start()
        self.context.rear_light.start()
        self.context.front_light.start()

        while self.running:
            # TODO: increase tick rate
            self.context.rear_light.on_tick(0.1)
            self.context.front_light.on_tick(0.1)
            time.sleep(0.1)

    def stop(self):
        self.running = False

class BusThread(threading.Thread):
    def __init__(self, context: SimulationContext):
        super().__init__()
        self.context = context
        self.running = True
        self.master = LineMaster(None, self.context.network)

    def run(self):
        with self.master:

            self.master.virtual_bus.add(self.context.body_computer)
            self.master.virtual_bus.add(self.context.rotor_sensor)
            self.master.virtual_bus.add(self.context.rear_light)
            self.master.virtual_bus.add(self.context.front_light)

            while self.running:
                time.sleep(0.1)

            self.master.disable_schedule()

    def stop(self):
        self.running = False
        #self.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication([])
    app.setApplicationName("Bicycle Simulation")
    window = QWidget()

    main_layout = QVBoxLayout()

    simulation_context = SimulationContext(load_network(os.path.join(os.path.dirname(__file__), '..', 'network.json')))
    simulation_context.setup()
    
    simulation_thread = SimulationThread(simulation_context)
    bus_thread = BusThread(simulation_context)

    def closeEvent(event):
        simulation_thread.stop()
        bus_thread.stop()
        event.accept()

    rear_light_panel = RearLightSimulationPanel(simulation_context.rear_light)
    rear_light_status_panel = RearLightStatusPanel(bus_thread.master, simulation_context.network)
    front_light_panel = FrontLightSimulationPanel(simulation_context.front_light)
    schedule_control = ScheduleControl(bus_thread.master, simulation_context.network.schedules)

    rear_light_diag = DiagnosticInfoView(bus_thread.master, [
        simulation_context.network.get_node('RearLight'),
        simulation_context.network.get_node('FrontLight')
    ])

    main_layout.addWidget(schedule_control)
    main_layout.addWidget(rear_light_panel)
    main_layout.addWidget(rear_light_status_panel)
    main_layout.addWidget(rear_light_diag)
    main_layout.addWidget(front_light_panel)

    simulation_thread.start()
    bus_thread.start()

    window.closeEvent = closeEvent
    window.setLayout(main_layout)
    window.show()
    app.exec()