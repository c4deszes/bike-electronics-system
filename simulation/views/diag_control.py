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

class DiagnosticControlView(QWidget):
    """
    A widget that displays the diagnostic status of a node.
    """

    def __init__(self, master: LineMaster, nodes: List[Node], parent=None):
        super().__init__(parent)
        self.master = master

        self.nodes = nodes

        self.main_layout = QVBoxLayout()

        self.group_box = QGroupBox('Diagnostic Information')
        self.group_layout = QVBoxLayout()
        self.group_box.setLayout(self.group_layout)

        self.node_selection = QComboBox()
        self.node_selection.addItem("All")
        self.node_selection.addItems([node.name for node in nodes])

        self.op_status_button = QPushButton("Operation Status")
        self.op_status_button.clicked.connect(self.request_opstatus)
        self.sw_number_button = QPushButton("Software Version")
        self.sw_number_button.clicked.connect(self.request_swversion)
        self.serial_number_button = QPushButton("Serial Number")
        self.serial_number_button.clicked.connect(self.request_serialnumber)

        self.group_layout.addWidget(self.node_selection)
        self.group_layout.addWidget(self.op_status_button)
        self.group_layout.addWidget(self.sw_number_button)
        self.group_layout.addWidget(self.serial_number_button)

        self.main_layout.addWidget(self.group_box)
        self.setLayout(self.main_layout)

    def request_opstatus(self):
        selected_node = self.node_selection.currentText()
        if selected_node == "All":
            for node in self.nodes:
                self.master.get_operation_status(node.address, wait=False)
        else:
            self.master.get_operation_status(selected_node, wait=False)

    def request_swversion(self):
        selected_node = self.node_selection.currentText()
        if selected_node == "All":
            for node in self.nodes:
                self.master.get_software_version(node.address, wait=False)
        else:
            self.master.get_software_version(selected_node, wait=False)

    def request_serialnumber(self):
        selected_node = self.node_selection.currentText()
        if selected_node == "All":
            for node in self.nodes:
                self.master.get_serial_number(node.address, wait=False)
        else:
            self.master.get_serial_number(selected_node, wait=False)
