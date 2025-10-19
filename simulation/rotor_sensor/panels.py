import time
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import DateAxisItem, InfiniteLine
from util.plotter import PlotView, SignalRef
from util.signal_view import SignalTable

from line_protocol.network import Network
from line_protocol.protocol.master import LineMaster, RequestListener, NodeStatusListener, Request

class RotorSensorSpeedPanel(QWidget):

    def __init__(self, master: LineMaster, network: Network, parent=None):
        super().__init__(parent)
        self.master = master

        self.speed_timestamp = []
        self.speed_data = []

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("RotorSensor speed")
        self.group_layout = QVBoxLayout()

        # Speed Graph
        self.speed_plot = PlotView("Speed", master, [
            network.get_signal('SpeedStatus', 'Speed'),
            network.get_signal('RotorSensorSpeedDebug', 'FrontSpeed'),
            network.get_signal('RotorSensorSpeedDebug', 'RearSpeed')
        ])

        self.group_layout.addWidget(self.speed_plot)

        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

class RotorSensorStatusPanel(QWidget):

    def __init__(self, master: LineMaster, network: Network, parent=None):
        super().__init__(parent)
        self.master = master

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("RotorSensor status")
        self.group_layout = QVBoxLayout()

        self.ride_monitor = SignalTable("Ride Monitor", master, [
            network.get_signal('RideStatus', 'RideStatus'),
            network.get_signal('RideStatus', 'Duration'),
            network.get_signal('RideStatus', 'DistanceStatus'),
            network.get_signal('RideStatus', 'Distance'),
        ])

        self.sensor_monitor = SignalTable("Sensor Monitor", master, [
            network.get_signal('RotorSensorSpeedDebug', 'FrontSensorStatus'),
            network.get_signal('RotorSensorSpeedDebug', 'RearSensorStatus'),
            network.get_signal('RotorSensorSpeedDebug', 'CrankSensorStatus')
        ])

        self.pressure_monitor = SignalTable("Pressure Monitor", master, [
            network.get_signal('RoadStatus', 'Altitude'),
            network.get_signal('RoadStatus', 'AltitudeError'),
            network.get_signal('RotorSensorPressureDebug', 'Pressure'),
            network.get_signal('RoadStatus', 'PressureError'),
        ])

        self.stats_view = SignalTable("Statistics", master, [
            network.get_signal('RideStatistics', 'TopSpeed'),
            network.get_signal('RideStatistics', 'AverageSpeed'),
        ])

        # Cadence graph

        self.group_layout.addWidget(self.ride_monitor)
        self.group_layout.addWidget(self.sensor_monitor)
        self.group_layout.addWidget(self.pressure_monitor)
        self.group_layout.addWidget(self.stats_view)

        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)
