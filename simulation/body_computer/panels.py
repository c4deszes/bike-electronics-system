import time
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

from line_protocol.protocol.simulation import SimulatedPeripheral

class BodyComputerControlPanel(QWidget):

    def __init__(self, peripheral: SimulatedPeripheral, parent=None):
        super().__init__(parent)
        self.peripheral = peripheral

        self.main_layout = QVBoxLayout()
        self.main_group = QGroupBox("BodyComputer Control")

        self.group_layout = QHBoxLayout()

        # Light main controls
        self.light_control_group = QGroupBox("Lights")
        self.light_control_layout = QGridLayout()
        self.light_control_group.setLayout(self.light_control_layout)

        self.light_mode_label = QLabel("Mode")
        self.light_mode_combo = QComboBox()
        # TODO: populate based on encoder
        self.light_mode_combo.addItems(['Adaptive', 'Standard', 'Emergency', 'Off'])
        self.light_mode_combo.currentTextChanged.connect(self.update_signals)

        self.brightness_label = QLabel("Brightness")
        self.brightness_slider = QSlider()
        self.brightness_slider.setOrientation(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_signals)

        self.light_control_layout.addWidget(self.light_mode_label, 0, 0)
        self.light_control_layout.addWidget(self.light_mode_combo, 0, 1)
        self.light_control_layout.addWidget(self.brightness_label, 1, 0)
        self.light_control_layout.addWidget(self.brightness_slider, 1, 1)

        # Front light control
        self.front_light_group = QGroupBox("Front Light Control")
        self.front_light_layout = QGridLayout()
        self.front_light_group.setLayout(self.front_light_layout)

        self.front_mode_label = QLabel("Front Light Mode")
        self.front_mode_combo = QComboBox()
        self.front_mode_combo.addItems(['Default', 'Solid', 'Blink', 'UNUSED'])
        self.front_mode_combo.currentTextChanged.connect(self.update_signals)

        self.front_light_layout.addWidget(self.front_mode_label, 0, 0)
        self.front_light_layout.addWidget(self.front_mode_combo, 0, 1)

        # Rear light control
        self.rear_light_group = QGroupBox("Rear Light Control")
        self.rear_light_layout = QGridLayout()
        self.rear_light_group.setLayout(self.rear_light_layout)

        self.rear_mode_label = QLabel("Rear Light Mode")
        self.rear_mode_combo = QComboBox()
        self.rear_mode_combo.addItems(['Default', 'Solid', 'Blink', 'UNUSED'])
        self.rear_mode_combo.currentTextChanged.connect(self.update_signals)
        self.rear_light_layout.addWidget(self.rear_mode_label, 0, 0)
        self.rear_light_layout.addWidget(self.rear_mode_combo, 0, 1)

        # Final layout assembly
        self.group_layout.addWidget(self.light_control_group)
        self.group_layout.addWidget(self.front_light_group)
        self.group_layout.addWidget(self.rear_light_group)
        self.main_group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.main_group)
        self.setLayout(self.main_layout)

    def update_signals(self):
        self.peripheral.requests.LightSynchronization.TargetBrightness = self.brightness_slider.value()
        self.peripheral.requests.LightSynchronization.LightMode = self.light_mode_combo.currentText()
        self.peripheral.requests.FrontLightSetting.Behavior = self.front_mode_combo.currentText()
        self.peripheral.requests.RearLightSetting.Behavior = self.rear_mode_combo.currentText()
