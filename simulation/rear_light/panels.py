import time
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

from line_protocol.protocol.master import LineMaster
from line_protocol.network import Network

from .model import RearLightSimulation, RearLightListener
from views.signal_view import SignalTable

class RearLightSimulationPanel(QWidget, RearLightListener):

    brightness_signal = pyqtSignal(int)

    def __init__(self, simulation: RearLightSimulation , parent=None):
        super().__init__(parent)

        self.simulation = simulation
        self.simulation.listener = self

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("Rear Light simulation")
        self.group_layout = QVBoxLayout()

        self.power_switch = QCheckBox("Power")
        self.power_switch.setChecked(True)
        self.power_switch.stateChanged.connect(self.power_change)

        self.bus_switch = QCheckBox("Bus")
        self.bus_switch.setChecked(True)
        self.bus_switch.stateChanged.connect(self.bus_change)

        self.brightness_label = QLabel("Brightness: 0%")
        self.brightness_signal.connect(lambda x: self.brightness_label.setText(f"Brightness: {x}%"))

        self.light_canvas_label = QLabel()
        light_scale = 3
        light_width = 33 * light_scale
        light_height = 63 * light_scale
        light_offset = 12 * light_scale
        light_size = 20 * light_scale
        self.light_canvas = QPixmap(light_width, light_height)
        self.light_canvas.fill(QColor(0, 0, 0, 0))
        self.draw_lightbody(light_width, light_height, light_offset, light_size)
        
        self.brightness_signal.connect(lambda brightness: self.update_light_brightness(light_height, light_width, light_offset, light_size, brightness))
        self.light_canvas_label.setPixmap(self.light_canvas)

        self.group_layout.addWidget(self.power_switch)
        self.group_layout.addWidget(self.bus_switch)
        self.group_layout.addWidget(self.brightness_label)
        self.main_layout.addWidget(self.light_canvas_label)
        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

    def power_change(self):
        # if self.power_switch.isChecked():
        #     if self.bus_switch.isChecked():
        #         self.simulation.connected = True
        #     else:
        #         self.simulation.connected = False
        # else:
        #     self.simulation.reset()
        #     self.simulation.connected = False
        pass

    def bus_change(self):
        if self.bus_switch.isChecked() and self.power_switch.isChecked():
            self.simulation.connected = True
        else:
            self.simulation.connected = False

    def draw_lightbody(self, light_width, light_height, light_offset, light_size):
        painter = QPainter(self.light_canvas)
        painter.setBrush(QColor(10, 10, 10))
        painter.drawRoundedRect(0, 0, light_width, light_height, light_width / 2, light_width / 2)
        painter.end()

        self.update_light_brightness(light_height, light_width, light_offset, light_size, 30)

        self.light_canvas_label.setPixmap(self.light_canvas)

    def update_light_brightness(self, light_height, light_width, light_offset, light_size, brightness):
        gray_value = int((brightness / 100) * (255 - 30) + 30)
        painter = QPainter(self.light_canvas)
        painter.setBrush(QColor(gray_value, 0, 0))
        painter.drawEllipse(int((light_width - light_size) / 2), light_offset, light_size, light_size)
        painter.end()

        self.light_canvas_label.setPixmap(self.light_canvas)

    def on_brightness_changed(self, brightness):
        self.brightness_signal.emit(brightness)

class RearLightStatusPanel(SignalTable):

    def __init__(self, master: LineMaster, network: Network, parent=None):
        super().__init__('RearLight status', master, 
                         [
                            network.get_signal("RearLightStatus", "TailLightStatus"),
                            network.get_signal("RearLightStatus", "BrakeLightStatus"),
                            network.get_signal("RearLightStatus", "TurnSignalLightStatus"),
                            network.get_signal("RearLightStatus", "ThermalStatus")
                         ], parent)

# class RearLightStatusPanel(QWidget, RequestListener, NodeStatusListener):
    
#     status_signal = pyqtSignal(dict)

#     def __init__(self, master: LineMaster, parent=None):
#         super().__init__(parent)

#         master.add_request_listener(self)

#         self.rearlight_status = {
#             'TailLightStatus': None,
#             'BrakeLightStatus': None,
#             'TurnSignalLightStatus': None,
#             'ThermalStatus': None
#         }

#         self.main_layout = QVBoxLayout()

#         self.group = QGroupBox("RearLight status")
#         self.signal_layout = QGridLayout()
        
#         self.tail_light_label = QLabel("TailLight")
#         self.tail_light_status = QLabel("")
#         self.brake_light_label = QLabel("BrakeLight")
#         self.brake_light_status = QLabel("")
#         self.turn_light_label = QLabel("TurnSignalLight")
#         self.turn_light_status = QLabel("")
#         self.thermal_status_label = QLabel("ThermalStatus")
#         self.thermal_status = QLabel("")

#         self.signal_layout.addWidget(self.tail_light_label, 0, 0)
#         self.signal_layout.addWidget(self.tail_light_status, 0, 1)
#         self.signal_layout.addWidget(self.brake_light_label, 1, 0)
#         self.signal_layout.addWidget(self.brake_light_status, 1, 1)
#         self.signal_layout.addWidget(self.turn_light_label, 2, 0)
#         self.signal_layout.addWidget(self.turn_light_status, 2, 1)
#         self.signal_layout.addWidget(self.thermal_status_label, 3, 0)
#         self.signal_layout.addWidget(self.thermal_status, 3, 1)

#         self.status_signal.connect(self.update_status)
#         self.update_status()

#         self.group.setLayout(self.signal_layout)
#         self.main_layout.addWidget(self.group)
#         self.setLayout(self.main_layout)

#     def update_status(self):
#         if self.rearlight_status['TailLightStatus'] is not None:
#             self.tail_light_status.setText(self.rearlight_status['TailLightStatus'])
#         else:
#             self.tail_light_status.setText("N/A")

#         if self.rearlight_status['BrakeLightStatus'] is not None:
#             self.brake_light_status.setText(self.rearlight_status['BrakeLightStatus'])
#         else:
#             self.brake_light_status.setText("N/A")

#         if self.rearlight_status.get('TurnSignalLightStatus') is not None:
#             self.turn_light_status.setText(self.rearlight_status['TurnSignalLightStatus'])
#         else:
#             self.turn_light_status.setText("N/A")

#         if self.rearlight_status.get('ThermalStatus') is not None:
#             self.thermal_status.setText(self.rearlight_status['ThermalStatus'])
#         else:
#             self.thermal_status.setText("N/A")

#     def on_user_request(self, timestamp: float, request: Request, signals) -> None:
#         if request.name == 'RearLightStatus':
#             self.rearlight_status = signals
#             self.status_signal.emit(self.rearlight_status)

#     def on_error(self, timestamp: float, request: Request, error_type):
#         if request.name == 'RearLightStatus':
#             self.rearlight_status = {
#                 'TailLightStatus': None,
#                 'BrakeLightStatus': None,
#                 'TurnSignalLightStatus': None,
#                 'ThermalStatus': None
#             }
#             self.status_signal.emit(self.rearlight_status)

#     # def on_node_status(self, node):
#     #     pass