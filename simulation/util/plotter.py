import time
from PyQt6.QtCore import QObject, pyqtSignal
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

    def __init__(self, name: str, master: LineMaster, signals: List[SignalRef], parent=None) -> None:
        super().__init__(parent)

        self.master = master
        self.master.add_request_listener(self)
        self.signals = signals

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

    def on_user_request(self, timestamp: float, request: Request, signals) -> None:
        for signal_ref in self.signals:
            if request.name == signal_ref.request.name:
                if signal_ref.signal.name in signals:
                    value = signals[signal_ref.signal.name]
                    series = self.data_series[signal_ref]
                    series.timestamps.append(time.time())
                    series.data.append(value)
                    series.plot.setData(
                        series.timestamps,
                        series.data
                    )

    def on_error(self, timestamp: float, request: Request, error_type):
        pass
