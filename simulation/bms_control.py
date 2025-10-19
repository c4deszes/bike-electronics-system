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
from body_computer import BodyComputerControlPanel
from rear_light import RearLightStatusPanel
from rotor_sensor import RotorSensorStatusPanel

# Utilities
from util.schedule_control import ScheduleControl

class SimulationContext:
    def __init__(self, network: Network):
        self.network = network

    def setup(self):
        self.body_computer = SimulatedPeripheral(self.network.get_node("BodyComputer"))

class SimulationThread(threading.Thread):
    def __init__(self, context: SimulationContext):
        super().__init__()
        self.context = context
        self.running = False

    def run(self):
        self.running = True

        while self.running:
            # TODO: increase tick rate
            time.sleep(0.1)

    def stop(self):
        self.running = False

class BusThread(threading.Thread):
    def __init__(self, context: SimulationContext):
        super().__init__()
        self.context = context
        self.running = True
        self.transport = LineSerialTransport('COM9', self.context.network.baudrate)
        self.master = LineMaster(self.transport, self.context.network)

    def run(self):
        with self.transport:
            with self.master:
                self.master.virtual_bus.add(self.context.body_computer)

                while self.running:
                    time.sleep(0.1)

                self.master.disable_schedule()

    def stop(self):
        self.running = False
        #self.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication([])
    app.setApplicationName("BodyComputer Control")
    window = QWidget()

    main_layout = QGridLayout()

    simulation_context = SimulationContext(load_network(os.path.join(os.path.dirname(__file__), '..', 'network.json')))
    simulation_context.setup()
    
    simulation_thread = SimulationThread(simulation_context)
    bus_thread = BusThread(simulation_context)

    def closeEvent(event):
        simulation_thread.stop()
        bus_thread.stop()
        event.accept()

    rear_light_status_panel = RearLightStatusPanel(bus_thread.master, simulation_context.network)
    rotor_sensor_status_panel = RotorSensorStatusPanel(bus_thread.master, simulation_context.network)
    body_computer_control_panel = BodyComputerControlPanel(simulation_context.body_computer)
    schedule_control = ScheduleControl(bus_thread.master, simulation_context.network.schedules)

    main_layout.addWidget(schedule_control, 0, 0)
    main_layout.addWidget(body_computer_control_panel, 1, 0)
    main_layout.addWidget(rear_light_status_panel, 2, 0)

    main_layout.addWidget(rotor_sensor_status_panel, 0, 1, 3, 1)

    simulation_thread.start()
    bus_thread.start()

    window.closeEvent = closeEvent
    window.setLayout(main_layout)
    window.show()
    app.exec()