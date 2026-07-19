import time
from dataclasses import dataclass
from typing import List, Any

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import DateAxisItem, InfiniteLine
from views.plotter import PlotView, SignalRef
from views.signal_view import SignalTable

from line_protocol.network import Network
from line_protocol.protocol.master import LineMaster, RequestListener, NodeStatusListener, Request, SignalValueContainer

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
            #network.get_signal('RotorSensorSpeedDebug', 'FrontSpeed'),
            #network.get_signal('RotorSensorSpeedDebug', 'RearSpeed')
        ])

        self.ride_monitor = SignalTable("Braking", master, [
            network.get_signal('SpeedStatus', 'BrakeState'),
        ])

        self.group_layout.addWidget(self.speed_plot)
        self.group_layout.addWidget(self.ride_monitor)

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
            network.get_signal('SpeedStatus', 'SpeedState'),

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
            network.get_signal('RoadStatus', 'Altitude')
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

@dataclass
class TimeSeries:
    plot: Any
    timestamps: List[float]
    data: List[Any]

class RotorSensorFullPanel(QWidget, RequestListener):

    def __init__(self, master: LineMaster, network: Network, parent=None):
        super().__init__(parent)
        self.master = master
        self.master.add_request_listener(self)

        self.main_layout = QVBoxLayout()

# Speed plots
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setLabel('left', 'Speed', units='km/h')
        self.plot_widget.setYRange(0, 50)
        self.plot_item = self.plot_widget.getPlotItem()

        # Create right Y-axis for cadence
        self.plot_item.showAxis('right')
        self.cadence_axis = self.plot_item.getAxis('right')
        self.cadence_view_box = pg.ViewBox()
        self.plot_widget.scene().addItem(self.cadence_view_box)
        self.cadence_axis.linkToView(self.cadence_view_box)
        self.cadence_view_box.setYRange(0, 200)
        self.cadence_axis.setLabel('Cadence', units='RPM')
        
        # Initialize TimeSeries
        self.speed_series = TimeSeries(
            plot=self.plot_widget.plot(pen='b', name='Speed'),
            timestamps=[],
            data=[]
        )
        
        cadence_pen = pg.mkPen('r')
        cadence_plot = pg.PlotCurveItem(pen=cadence_pen, name='Cadence')
        self.cadence_view_box.addItem(cadence_plot)
        self.cadence_series = TimeSeries(
            plot=cadence_plot,
            timestamps=[],
            data=[]
        )

        self.front_speed_series = TimeSeries(
            plot=self.plot_widget.plot(pen='g', name='Front Speed'),
            timestamps=[],
            data=[]
        )

        # Link x-axis and keep view geometry in sync.
        self.cadence_view_box.setXLink(self.plot_item.vb)
        self.plot_item.vb.sigResized.connect(self._update_cadence_view_geometry)
        self._update_cadence_view_geometry()

# Ride status table
        self.ride_status = QLabel(network.get_signal('RideStatus', 'RideStatus').signal.initial)
        self.ride_duration = QLabel(str(network.get_signal('RideStatus', 'Duration').signal.initial))
        self.ride_distance_status = QLabel(network.get_signal('RideStatus', 'DistanceStatus').signal.initial)
        self.ride_distance = QLabel(str(network.get_signal('RideStatus', 'Distance').signal.initial))

        self.main_layout.addWidget(self.plot_widget)
        self.main_layout.addWidget(self.ride_status)
        self.main_layout.addWidget(self.ride_duration)
        self.main_layout.addWidget(self.ride_distance_status)
        self.main_layout.addWidget(self.ride_distance)

        self.setLayout(self.main_layout)

    def _update_cadence_view_geometry(self) -> None:
        self.cadence_view_box.setGeometry(self.plot_item.vb.sceneBoundingRect())
        self.cadence_view_box.linkedViewChanged(self.plot_item.vb, self.cadence_view_box.XAxis)

    def on_user_request(self, timestamp: float, request: Request, buffer: List[int], signals: SignalValueContainer) -> None:
        if request.name == 'SpeedStatus':
            global_speed = signals['Speed'].phy
            self.speed_series.timestamps.append(timestamp)
            self.speed_series.data.append(global_speed)
            self.speed_series.plot.setData(
                self.speed_series.timestamps,
                self.speed_series.data
            )

        if request.name == 'DrivetrainStatus':
            crank_speed = signals['Cadence'].phy

            cadence = crank_speed
            self.cadence_series.timestamps.append(timestamp)
            self.cadence_series.data.append(cadence)
            self.cadence_series.plot.setData(
                self.cadence_series.timestamps,
                self.cadence_series.data
            )

        if request.name == 'RideStatus':
            self.ride_status.setText(str(signals['RideStatus'].phy))
            self.ride_duration.setText(str(signals['Duration'].phy))
            self.ride_distance_status.setText(str(signals['DistanceStatus'].phy))
            self.ride_distance.setText(str(signals['Distance'].phy))

        if request.name == 'RotorSensorSpeedDebug':
            front_speed = signals['FrontSpeed'].phy
            self.front_speed_series.timestamps.append(timestamp)
            self.front_speed_series.data.append(front_speed)
            self.front_speed_series.plot.setData(
                self.front_speed_series.timestamps,
                self.front_speed_series.data
            )

    def on_error(self, timestamp: float, request: Request, error_type):
        pass
