import time
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import DateAxisItem, InfiniteLine
from util.plotter import PlotView, SignalRef, SignalTable

from line_protocol.protocol.master import LineMaster, RequestListener, NodeStatusListener

class RotorSensorStatusPanel(QWidget, RequestListener, NodeStatusListener):

    def __init__(self, master: LineMaster, network, parent=None):
        super().__init__(parent)
        self.master = master

        self.speed_timestamp = []
        self.speed_data = []

        self.cadence_timestamp = []
        self.cadence_data = []

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("RotorSensor status")
        self.group_layout = QVBoxLayout()

        # Speed Graph
        speed_status = network.get_request('SpeedStatus')
        speed_sensor_debug = network.get_request('RotorSensorSpeedDebug')
        pressure_debug = network.get_request('RotorSensorPressureDebug')
        road_status = network.get_request('RoadStatus')
        ride_status = network.get_request('RideStatus')
        ride_statistics = network.get_request('RideStatistics')

        self.speed_plot = PlotView("Speed", master, [
            SignalRef(speed_status, speed_status.get_signal('Speed')),
            SignalRef(speed_sensor_debug, speed_sensor_debug.get_signal('FrontSpeed')),
            SignalRef(speed_sensor_debug, speed_sensor_debug.get_signal('RearSpeed'))
        ])

        self.ride_monitor = SignalTable("Ride Monitor", master, [
            SignalRef(ride_status, ride_status.get_signal('RideStatus')),
            SignalRef(ride_status, ride_status.get_signal('Duration')),
            SignalRef(ride_status, ride_status.get_signal('DistanceStatus')),
            SignalRef(ride_status, ride_status.get_signal('Distance')),
        ])

        self.sensor_monitor = SignalTable("Sensor Monitor", master, [
            SignalRef(speed_sensor_debug, speed_sensor_debug.get_signal('FrontSensorStatus')),
            SignalRef(speed_sensor_debug, speed_sensor_debug.get_signal('RearSensorStatus')),
            SignalRef(speed_sensor_debug, speed_sensor_debug.get_signal('CrankSensorStatus'))
        ])

        self.pressure_monitor = SignalTable("Pressure Monitor", master, [
            SignalRef(road_status, road_status.get_signal('Altitude')),
            SignalRef(road_status, road_status.get_signal('AltitudeError')),
            SignalRef(pressure_debug, pressure_debug.get_signal('Pressure')),
            SignalRef(road_status, road_status.get_signal('PressureError')),
        ])

        self.stats_view = SignalTable("Statistics", master, [
            SignalRef(ride_statistics, ride_statistics.get_signal('TopSpeed')),
            SignalRef(ride_statistics, ride_statistics.get_signal('AverageSpeed')),
        ])

        # Cadence graph

        self.group_layout.addWidget(self.speed_plot)
        self.group_layout.addWidget(self.ride_monitor)
        self.group_layout.addWidget(self.sensor_monitor)
        self.group_layout.addWidget(self.pressure_monitor)
        self.group_layout.addWidget(self.stats_view)

        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

    def on_request(self, request, signals):
        pass

    def on_error(self, request, error_type):
        if request.name == 'RearLightStatus':
            pass