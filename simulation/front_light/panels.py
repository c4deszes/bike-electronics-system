from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

from .model import FrontLightSimulation, FrontLightListener

class FrontLightSimulationPanel(QWidget, FrontLightListener):

    brightness_signal = pyqtSignal(int)

    def __init__(self, simulation: FrontLightSimulation, parent=None):
        super().__init__(parent)

        self.simulation = simulation
        self.simulation.listener = self

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("Front Light")
        self.group_layout = QVBoxLayout()

        self.brightness_label = QLabel("Brightness: 0%")
        self.brightness_signal.connect(lambda x: self.brightness_label.setText(f"Brightness: {x}%"))
        
        self.user_button = QPushButton("Set Brightness")
        self.user_button.clicked.connect(lambda: self.simulation.press_button())

        self.group_layout.addWidget(self.brightness_label)
        self.group_layout.addWidget(self.user_button)
        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)

        self.setLayout(self.main_layout)

    def on_brightness_changed(self, brightness: int):
        self.brightness_signal.emit(brightness)
