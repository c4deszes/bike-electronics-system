import time
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import *

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph import DateAxisItem, InfiniteLine
from dataclasses import dataclass
from typing import List, Any

from line_protocol.protocol.master import LineMaster, RequestListener, NodeStatusListener, NodeStatus
from line_protocol.network import Request, SignalRef, FormulaEncoder, Node, NodeRef

@dataclass
class TimeSeries:
    plot: Any
    timestamps: List[float]
    data: List[Any]

class PlotView(QWidget, RequestListener):

    sample_received = pyqtSignal(float, object, object)

    def __init__(self, name: str, master: LineMaster, signals: List[SignalRef], parent=None) -> None:
        super().__init__(parent)

        self.master = master
        self.master.add_request_listener(self)
        self.signals = signals
        self.max_points = 3000
        self.window_seconds = 30.0

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox(name)
        self.group_layout = QVBoxLayout()

        self.plot_widget = pg.PlotWidget()
        self.data_series = {
            signal_ref: TimeSeries(self.plot_widget.plot(pen=(i, len(self.signals))), [], [])
            for i, signal_ref in enumerate(self.signals)
        }
        self.plot_widget.showGrid(x=True, y=True)

        self.group_layout.addWidget(self.plot_widget)
        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)

        self.setLayout(self.main_layout)

        self.sample_received.connect(self._append_sample)

    @pyqtSlot(float, object, object)
    def _append_sample(self, timestamp: float, signal_ref: SignalRef, value: Any) -> None:
        series = self.data_series[signal_ref]
        series.timestamps.append(timestamp)
        series.data.append(value)

        if len(series.timestamps) > self.max_points:
            del series.timestamps[:-self.max_points]
            del series.data[:-self.max_points]

        series.plot.setData(series.timestamps, series.data)
        self.plot_widget.setXRange(timestamp - self.window_seconds, timestamp, padding=0.0)

    def on_user_request(self, timestamp: float, request: Request, buffer: List[int], signals) -> None:
        for signal_ref in self.signals:
            if request.name == signal_ref.request.name:
                if signal_ref.signal.name in signals:
                    value = signals[signal_ref.signal.name].phy
                    self.sample_received.emit(time.time(), signal_ref, value)

    def on_error(self, timestamp: float, request: Request, error_type):
        pass
