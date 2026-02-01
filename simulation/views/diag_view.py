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

class DiagnosticInfoView(QWidget, NodeStatusListener):
    """
    A widget that displays the diagnostic status of a node.
    """

    signal = pyqtSignal(NodeRef, NodeStatus)

    def __init__(self, master: LineMaster, nodes: List[Node], parent=None):
        super().__init__(parent)
        self.master = master
        self.master.add_node_status_listener(self)

        self.main_layout = QVBoxLayout()

        self.labels = {}

        for node in nodes:
            group = QGroupBox(f'Diag - {node.name} (0x{node.address:01X})')
            op_status_label = QLabel("N/A")
            sw_number_label = QLabel("N/A")
            serial_number_label = QLabel("N/A")

            self.labels[node.address] = {
                'op_status': op_status_label,
                'sw_number': sw_number_label,
                'serial_number': serial_number_label
            }

            group_layout = QHBoxLayout()
            group_layout.addWidget(op_status_label)
            group_layout.addWidget(sw_number_label)
            group_layout.addWidget(serial_number_label)
            group.setLayout(group_layout)
            self.main_layout.addWidget(group)

        self.signal.connect(self.update_labels)
        self.setLayout(self.main_layout)

    def update_labels(self, ref, node_status):
        if ref.address in self.labels:
            labels = self.labels[ref.address]
            labels['op_status'].setText(f"{node_status.op_status if node_status.op_status is not None else 'N/A'}")
            labels['sw_number'].setText(f"{node_status.software_version if node_status.software_version is not None else 'N/A'}")
            labels['serial_number'].setText(f"0x{node_status.serial_number:08X}" if node_status.serial_number is not None else "N/A")

    def on_node_change(self, timestamp, ref, node, property) -> None:
        self.signal.emit(ref, node)
