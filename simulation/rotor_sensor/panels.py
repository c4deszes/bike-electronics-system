import time
from dataclasses import dataclass
from typing import List, Any

from PyQt6.QtCore import pyqtSignal, pyqtSlot
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
            network.get_signal('RideStatus', 'Speed'),
        ])

        self.ride_monitor = SignalTable("Braking", master, [
            network.get_signal('RideStatus', 'BrakeState'),
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
            network.get_signal('RideStatus', 'SpeedState'),

            network.get_signal('RideStatus', 'RideStatus'),
            network.get_signal('RideStatus', 'Duration'),
            network.get_signal('RideStatus', 'DistanceStatus'),
            network.get_signal('RideStatus', 'Distance'),
        ])

        self.pressure_monitor = SignalTable("Pressure Monitor", master, [
            network.get_signal('RoadStatus', 'Altitude'),
            network.get_signal('RoadStatus', 'Pressure')
        ])

        # Cadence graph

        self.group_layout.addWidget(self.ride_monitor)
        self.group_layout.addWidget(self.pressure_monitor)

        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

@dataclass
class TimeSeries:
    plot: Any
    timestamps: List[float]
    data: List[Any]

class RotorSensorFullPanel(QWidget, RequestListener):

    speed_received = pyqtSignal(float, float)
    cadence_received = pyqtSignal(float, float)
    period_received = pyqtSignal(float, float)
    ride_status_received = pyqtSignal(object, object, object, object)

    def __init__(self, master: LineMaster, network: Network, parent=None):
        super().__init__(parent)
        self.master = master
        self.master.add_request_listener(self)
        self.max_points = 3000
        self.window_seconds = 30.0

        self.main_layout = QVBoxLayout()

# Speed plots
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
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
        self.cadence_view_box.setMouseEnabled(x=False, y=False)
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

        # Link x-axis and keep view geometry in sync.
        self.cadence_view_box.setXLink(self.plot_item.vb)
        self.plot_item.vb.sigResized.connect(self._update_cadence_view_geometry)
        self._update_cadence_view_geometry()

# Ride status table
        self.ride_status = QLabel(network.get_signal('RideStatus', 'RideState').signal.initial)
        self.ride_duration = QLabel(str(network.get_signal('RideStatus', 'Duration').signal.initial))
        self.ride_distance_status = QLabel(network.get_signal('RideStatus', 'DistanceState').signal.initial)
        self.ride_distance = QLabel(str(network.get_signal('RideStatus', 'Distance').signal.initial))

        self.braking = QLabel(network.get_signal('RideStatus', 'BrakeState').signal.initial)

        self.main_layout.addWidget(self.plot_widget)
        self.main_layout.addWidget(self.ride_status)
        self.main_layout.addWidget(self.ride_duration)
        self.main_layout.addWidget(self.ride_distance_status)
        self.main_layout.addWidget(self.ride_distance)
        self.main_layout.addWidget(self.braking)

        self.setLayout(self.main_layout)

        self.speed_received.connect(self._append_speed)
        self.cadence_received.connect(self._append_cadence)
        self.period_received.connect(self._append_period)
        self.ride_status_received.connect(self._update_ride_status)

    def _trim_series(self, series: TimeSeries) -> None:
        if len(series.timestamps) > self.max_points:
            del series.timestamps[:-self.max_points]
            del series.data[:-self.max_points]

    def _update_time_window(self, timestamp: float) -> None:
        self.plot_widget.setXRange(timestamp - self.window_seconds, timestamp, padding=0.0)

    @pyqtSlot(float, float)
    def _append_speed(self, timestamp: float, value: float) -> None:
        self.speed_series.timestamps.append(timestamp)
        self.speed_series.data.append(value)
        self._trim_series(self.speed_series)
        self.speed_series.plot.setData(self.speed_series.timestamps, self.speed_series.data)
        self._update_time_window(timestamp)

    @pyqtSlot(float, float)
    def _append_cadence(self, timestamp: float, value: float) -> None:
        self.cadence_series.timestamps.append(timestamp)
        self.cadence_series.data.append(value)
        self._trim_series(self.cadence_series)
        self.cadence_series.plot.setData(self.cadence_series.timestamps, self.cadence_series.data)
        self._update_time_window(timestamp)

    @pyqtSlot(object, object, object, object)
    def _update_ride_status(self, ride_status: Any, duration: Any, distance_status: Any, distance: Any) -> None:
        self.ride_status.setText(str(ride_status))
        self.ride_duration.setText(str(duration))
        self.ride_distance_status.setText(str(distance_status))
        self.ride_distance.setText(str(distance))

    def _update_cadence_view_geometry(self) -> None:
        self.cadence_view_box.setGeometry(self.plot_item.vb.sceneBoundingRect())
        self.cadence_view_box.linkedViewChanged(self.plot_item.vb, self.cadence_view_box.XAxis)

    @pyqtSlot(float, float)
    def _append_period(self, front_period: float, rear_period: float) -> None:
        self.front_period.setText(str(front_period))
        self.rear_period.setText(str(rear_period))

    def on_user_request(self, timestamp: float, request: Request, buffer: List[int], signals: SignalValueContainer) -> None:
        if request.name == 'RideStatus':
            global_speed = signals['Speed'].phy
            brake_state = signals['BrakeState'].phy
            self.speed_received.emit(timestamp, global_speed)
            self.braking.setText(str(brake_state))

        if request.name == 'RideStatus':
            crank_speed = signals['Cadence'].phy

            cadence = crank_speed
            self.cadence_received.emit(timestamp, cadence)

        if request.name == 'RideStatus':
            self.ride_status_received.emit(
                signals['RideState'].phy,
                signals['Duration'].phy,
                signals['DistanceState'].phy,
                signals['Distance'].phy,
            )

    def on_error(self, timestamp: float, request: Request, error_type):
        pass
