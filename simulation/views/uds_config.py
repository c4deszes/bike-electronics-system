from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIntValidator

from typing import Any, List, Dict, Tuple, Union
from enum import Enum

from line_protocol.network.nodes import Node
from line_uds.uds_tool import UdsNodeStatus, UdsTool, UdsNodeStatusListener, UdsPropertyValue
from line_uds.profile import UdsProfile, UdsProperty, UdsService, UdsServiceParam, UdsBoolTypeDefinition, UdsIntTypeDefinition, UdsEnumTypeDefinition, UdsTypeDefinition, UdsVoidTypeDefinition

import logging
logger = logging.getLogger(__name__)

class UdsPropertyStatus(Enum):
    SYNC = 1
    CHANGED = 2
    UNKNOWN = 3
    ERROR = 4

class UdsPropertyStatusIndicator(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.set_status(UdsPropertyStatus.UNKNOWN)

    def set_status(self, status: UdsPropertyStatus):
        color = {
            UdsPropertyStatus.SYNC: "green",
            UdsPropertyStatus.CHANGED: "orange",
            UdsPropertyStatus.UNKNOWN: "gray",
            UdsPropertyStatus.ERROR: "red"
        }.get(status, "red")
        self.setStyleSheet(f"QLabel {{ background-color: {color}; }}")

class UdsNumericInput(QWidget):
    
    sig_changed = pyqtSignal(int)

    def __init__(self, value: int = 0, min_value: int = 0, max_value: int = 100):
        super().__init__()
        self._input = QLineEdit(self)
        self._input.setText(str(value))
        self._input.editingFinished.connect(self.on_editing_finished)
        validator = QIntValidator()
        validator.setRange(min_value, max_value)
        self._input.setValidator(validator)

        layout = QHBoxLayout()
        layout.addWidget(self._input)
        self.setLayout(layout)

    def set_value(self, value):
        self._input.setText(str(value))

    def get_value(self):
        return int(self._input.text())

    def on_editing_finished(self):
        try:
            value = int(self._input.text())
            self.sig_changed.emit(value)
        except ValueError:
            pass

class UdsBooleanInput(QWidget):
    
    sig_changed = pyqtSignal(bool)

    def __init__(self, value: bool = False):
        super().__init__()
        self._checkbox = QCheckBox(self)
        self._checkbox.setChecked(value)
        self._checkbox.stateChanged.connect(self.on_state_changed)

        layout = QHBoxLayout()
        layout.addWidget(self._checkbox)
        self.setLayout(layout)

    def set_value(self, value):
        self._checkbox.setChecked(value)

    def get_value(self):
        return self._checkbox.isChecked()

    def on_state_changed(self, state):
        self.sig_changed.emit(self._checkbox.isChecked())

class UdsEnumInput(QWidget):
    
    sig_changed = pyqtSignal(str)

    def __init__(self, options: List[str], value: str = None):
        super().__init__()
        self._combobox = QComboBox(self)
        for option in options:
            self._combobox.addItem(option)
        if value is not None:
            self._combobox.setCurrentIndex(self._combobox.findText(value))
        self._combobox.currentIndexChanged.connect(self.on_index_changed)

        layout = QHBoxLayout()
        layout.addWidget(self._combobox)
        self.setLayout(layout)

    def set_value(self, value):
        self._combobox.setCurrentIndex(self._combobox.findText(value))

    def get_value(self):
        return self._combobox.currentText()

    def on_index_changed(self, index):
        value = self._combobox.itemText(index)
        self.sig_changed.emit(value)

class UdsStructInput(QWidget):
    # For simplicity, we will just display a placeholder for struct inputs
    def __init__(self):
        super().__init__()
        label = QLabel("Struct input not implemented", self)
        layout = QHBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

class UdsPropertyInput(QWidget):

    sig_changed = pyqtSignal(UdsProperty, object)

    def __init__(self, property: UdsProperty, value: any = None):
        super().__init__()
        self._prop = property
        initial_value = value if value is not None else self._prop.default_value

        if isinstance(self._prop.typedef, UdsIntTypeDefinition):
            self._input = UdsNumericInput(initial_value, self._prop.min, self._prop.max)
            self._input.sig_changed.connect(lambda val: self.sig_changed.emit(self._prop, val))
        elif isinstance(self._prop.typedef, UdsBoolTypeDefinition):
            self._input = UdsBooleanInput(initial_value)
            self._input.sig_changed.connect(lambda val: self.sig_changed.emit(self._prop, val))
        elif isinstance(self._prop.typedef, UdsEnumTypeDefinition):
            self._input = UdsEnumInput(self._prop.typedef.values, initial_value)
            self._input.sig_changed.connect(lambda val: self.sig_changed.emit(self._prop, val))
        else:
            self._input = UdsStructInput()

        layout = QHBoxLayout()
        layout.addWidget(QLabel(self._prop.prop_name, self))
        layout.addWidget(self._input)
        self.setLayout(layout)

    def get_value(self):
        return self._input.get_value()
    
    def set_value(self, value):
        self._input.set_value(value)

class UdsPropertyTableView(QWidget):

    def __init__(self, properties: List[UdsProperty]):
        super().__init__()
        self.property_views: Dict[UdsProperty, UdsPropertyInput] = {}

        layout = QVBoxLayout()

        for i, prop in enumerate(properties):
            prop_input = UdsPropertyInput(prop)
            #prop_input.sig_changed.connect(self.on_property_changed)
            self.property_views[prop] = prop_input

            row_layout = QHBoxLayout()
            row_layout.addWidget(prop_input)
            layout.addLayout(row_layout)

        self.setLayout(layout)

    def get_property_values(self) -> Dict[UdsProperty, any]:
        values = {}
        for prop, view in self.property_views.items():
            values[prop] = view.get_value()
        return values

    def update_properties(self, properties: Dict[UdsProperty, any]):
        for prop, value in properties.items():
            if prop in self.property_views:
                view = self.property_views[prop]
                view.set_value(value)

class UdsPropertyEditor(QWidget, UdsNodeStatusListener):
    def __init__(self, node: Node, profile: UdsProfile, tool: UdsTool = None):
        super().__init__()
        self.node = node
        self.profile = profile
        self.tool = tool
        self.tool.add_listener(self)

        self.tables: Dict[str, UdsPropertyTableView] = {}

        tabs = QTabWidget(self)

        for group in profile.get_property_groups():
            table_view = UdsPropertyTableView(profile.get_properties_by_group(group))
            self.tables[group] = table_view
            scroll_layout = QVBoxLayout()
            scroll_layout.addWidget(table_view)
            scroll_layout.addStretch()
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(QWidget())
            scroll_area.widget().setLayout(scroll_layout)
            tabs.addTab(scroll_area, group)

        grid_layout = QGridLayout()

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send)
        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load)

        grid_layout.addWidget(send_button, 0, 0)
        grid_layout.addWidget(load_button, 0, 1)

        progress = QProgressBar()
        grid_layout.addWidget(progress, 1, 0, 1, 2)

        main_layout = QVBoxLayout()
        main_layout.addWidget(tabs)
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def send(self):
        for group, table_view in self.tables.items():
            for prop, value in table_view.get_property_values().items():
                self.tool.set_property(self.node.address, prop.prop_id, value)

    def load(self):
        for group, table_view in self.tables.items():
            for prop in table_view.property_views.keys():
                self.tool.get_property(self.node.address, prop.prop_id)

    def on_property_change(self, node, prop: UdsProperty, data: UdsPropertyValue):
        for group, table_view in self.tables.items():
            table_view.update_properties({prop: data.value})

class UdsServiceParamInput(QWidget):
    
    sig_changed = pyqtSignal(UdsServiceParam, object)

    def __init__(self, param: UdsServiceParam):
        super().__init__()
        self.param = param
        if isinstance(self.param.param_type, UdsIntTypeDefinition):
            # TODO: set min/max values based on type definition
            self._input = UdsNumericInput(0, 0, 100)
            self._input.sig_changed.connect(lambda val: self.sig_changed.emit(self.param, val))
        elif isinstance(self.param.param_type, UdsBoolTypeDefinition):
            self._input = UdsBooleanInput(False)
            self._input.sig_changed.connect(lambda val: self.sig_changed.emit(self.param, val))
        elif isinstance(self.param.param_type, UdsEnumTypeDefinition):
            self._input = UdsEnumInput(self.param.param_type.values, self.param.param_type.values[0])
            self._input.sig_changed.connect(lambda val: self.sig_changed.emit(self.param, val))
        else:
            self._input = UdsStructInput()

        layout = QHBoxLayout()
        layout.addWidget(QLabel(param.param_name, self))
        layout.addWidget(self._input)
        self.setLayout(layout)

    def get_value(self):
        return self._input.get_value()

class UdsServiceParamTableView(QWidget):

    def __init__(self, params: List[UdsServiceParam]):
        super().__init__()
        self.param_views: Dict[UdsServiceParam, UdsServiceParamInput] = {}

        layout = QVBoxLayout()

        for i, param in enumerate(params):
            param_input = UdsServiceParamInput(param)
            #param_input.sig_changed.connect(self.on_param_changed)
            self.param_views[param] = param_input

            row_layout = QHBoxLayout()
            row_layout.addWidget(param_input)
            layout.addLayout(row_layout)

        self.setLayout(layout)

    def get_param_values(self) -> Dict[UdsServiceParam, any]:
        values = {}
        for param, view in self.param_views.items():
            values[param] = view.get_value()
        return values
    
class UdsServiceResultView(QWidget):
    
    def __init__(self, return_type: UdsTypeDefinition):
        super().__init__()
        self.return_type = return_type
        
        self.return_value = QTextEdit()
        self.return_value.setReadOnly(True)

        self.return_code = QLineEdit()
        self.return_code.setDisabled(True)

        layout = QVBoxLayout()
        status_box = QHBoxLayout()
        status_box.addWidget(QLabel("Status:"))
        status_box.addWidget(self.return_code)
        layout.addLayout(status_box)

        if not isinstance(return_type, UdsVoidTypeDefinition):
            layout.addWidget(self.return_value)
        self.setLayout(layout)

    def update_result(self, result):
        self.return_value.setText(str(result))

class UdsServiceView(QWidget):

    sig_call_service = pyqtSignal(UdsService, dict)
    
    def __init__(self, service: UdsService):
        super().__init__()
        self.service = service
        label = QLabel(f"Service {self.service.service_id}: {self.service.name}", self)

        self.param_table = UdsServiceParamTableView(self.service.params)
        self.result_view = UdsServiceResultView(self.service.return_type)

        # Params
        param_view = QVBoxLayout()
        param_group = QGroupBox("Parameters")
        param_view.addWidget(self.param_table)
        param_group.setLayout(param_view)

        results_view = QVBoxLayout()
        results_group = QGroupBox("Results")
        results_group.setLayout(results_view)
        results_view.addWidget(self.result_view)

        call_button = QPushButton("Call Service")
        call_button.clicked.connect(self.do_call_service)
        # TODO: Implement service call logic and update result view with response

        main_layout = QVBoxLayout()
        main_layout.addWidget(label)
        if len(self.service.params) > 0:
            main_layout.addWidget(param_group)
        main_layout.addWidget(results_group)
        main_layout.addWidget(call_button)
        self.setLayout(main_layout)

    def do_call_service(self):
        param_values = self.param_table.get_param_values()
        self.sig_call_service.emit(self.service, param_values)

class UdsServiceInterface(QWidget):

    def __init__(self, node: Node, profile: UdsProfile, tool: UdsTool = None):
        super().__init__()
        self.node = node
        self.profile = profile
        self.tool = tool
        
        tabs = QTabWidget(self)
        
        for group in profile.get_service_groups():
            group_services = [service for service in profile.services if service.group == group]
            group_widget = QWidget()
            group_layout = QVBoxLayout()
            for service in group_services:
                service_view = UdsServiceView(service)
                service_view.sig_call_service.connect(self.call_service)
                group_layout.addWidget(service_view)
            group_layout.addStretch()
            group_widget.setLayout(group_layout)
            tabs.addTab(group_widget, group)

        main_layout = QHBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

    def call_service(self, service: UdsService, params: dict):
        self.tool.call_service(self.node.address, service.service_id, {param.param_name: value for param, value in params.items()})

class UdsNodeEditor(QWidget):

    def __init__(self, node: Node, profile: UdsProfile, tool: UdsTool = None):
        super().__init__()
        self.node = node
        self.profile = profile
        self.tool = tool

        main_layout = QHBoxLayout()
        self.property_editor = UdsPropertyEditor(node, profile, tool)
        self.service_panel = UdsServiceInterface(node, profile, tool)
        main_layout.addWidget(self.property_editor)
        main_layout.addWidget(self.service_panel)
        self.setLayout(main_layout)

class UdsNodesEditor(QWidget):

    def __init__(self, nodes: Dict[Node, UdsProfile], tool: UdsTool = None):
        super().__init__()
        self.tool = tool
        self.node_editors = {}
        tabs = QTabWidget(self)
        for node, profile in nodes.items():
            editor = UdsNodeEditor(node, profile, tool)
            self.node_editors[node] = editor
            tabs.addTab(editor, node.name)
        main_layout = QHBoxLayout()
        main_layout.addWidget(tabs)
        self.setLayout(main_layout)
