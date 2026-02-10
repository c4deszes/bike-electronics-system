import time
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

from line_protocol.protocol.master import LineMaster
from line_protocol.network import Network

from .model import RearLightSimulation, RearLightListener
from views.signal_view import SignalTable

LIGHT_WIDTH = 33
LIGHT_HEIGHT = 63
LIGHT_OFFSET = 12
LIGHT_SIZE = 20
LIGHTBODY_COLOR = QColor(20, 20, 20)
MIN_BRIGHTNESS_COLOR = 30

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

        self.light_canvas_label = QLabel()

        light_scale = 3
        light_width = LIGHT_WIDTH * light_scale
        light_height = LIGHT_HEIGHT * light_scale
        light_offset = LIGHT_OFFSET * light_scale
        light_size = LIGHT_SIZE * light_scale

        self.light_canvas = QPixmap(light_width, light_height)
        self.light_canvas.fill(QColor(0, 0, 0, 0))
        self.draw_lightbody(self.light_canvas, light_width, light_height, light_offset, light_size)
        
        self.brightness_signal.connect(lambda brightness: self.update_light_brightness(self.light_canvas, light_height, light_width, light_offset, light_size, brightness))
        self.light_canvas_label.setPixmap(self.light_canvas)

        self.group_layout.addWidget(self.power_switch)
        self.group_layout.addWidget(self.bus_switch)
        self.main_layout.addWidget(self.light_canvas_label)
        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

    def power_change(self):
        # TODO: powerdown the simulation
        pass

    def bus_change(self):
        # TODO: disconnect the simulation from the bus
        if self.bus_switch.isChecked() and self.power_switch.isChecked():
            self.simulation.connected = True
        else:
            self.simulation.connected = False

    def draw_lightbody(self, canvas, light_width, light_height, light_offset, light_size):
        painter = QPainter(canvas)
        painter.setBrush(LIGHTBODY_COLOR)
        painter.drawRoundedRect(0, 0, light_width, light_height, light_width / 2, light_width / 2)
        painter.end()

        self.update_light_brightness(canvas, light_height, light_width, light_offset, light_size, 0)
        self.light_canvas_label.setPixmap(self.light_canvas)

    def update_light_brightness(self, canvas, light_height, light_width, light_offset, light_size, brightness):
        gray_value = int((brightness / 100) * (255 - MIN_BRIGHTNESS_COLOR) + MIN_BRIGHTNESS_COLOR)
        painter = QPainter(canvas)
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
