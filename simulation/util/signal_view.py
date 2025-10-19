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

class SignalTable(QWidget, RequestListener):
    """
    A widget that displays a table of signals for a given request.
    """

    def __init__(self, name: str, master: LineMaster, signals: List[SignalRef], parent=None):
        super().__init__(parent)
        self.master = master
        self.master.add_request_listener(self)

        self.signals = signals

        self.main_layout = QVBoxLayout()
        self.group = QGroupBox(name)
        self.signal_table = QGridLayout()

        self.signal_labels = {
            signal_ref: QLabel(f"N/A")
            for signal_ref in signals
        }

        cnt = 0
        for ref, label in self.signal_labels.items():
            self.signal_table.addWidget(QLabel(f"{ref.request.name}.{ref.signal.name}"), cnt, 0)
            self.signal_table.addWidget(label, cnt, 1)
            cnt += 1

        self.group.setLayout(self.signal_table)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

    def on_user_request(self, timestamp: float, request: Request, signals) -> None:
        for signal_ref in self.signals:
            if request.name == signal_ref.request.name:
                if signal_ref.signal.name in signals:
                    value = signals[signal_ref.signal.name].phy
                    label = self.signal_labels[signal_ref]

                    if isinstance(signal_ref.signal.encoder, FormulaEncoder):
                        label.setText(f"{value:.03f} {signal_ref.signal.encoder.unit}")
                    else:
                        label.setText(str(value))

    def on_error(self, timestamp: float, request: Request, error_type):
        pass