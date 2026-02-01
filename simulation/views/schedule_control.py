
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *

class ScheduleControl(QWidget):

    def __init__(self, master, schedules, parent=None):
        super().__init__(parent)

        self.active = False
        self.master = master

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("Schedule control")
        self.group_layout = QHBoxLayout()

        self.schedule_select = QComboBox()
        self.schedule_select.addItems([x.name for x in schedules])

        self.schedule_control = QPushButton("Start")
        self.schedule_control.clicked.connect(lambda: self.toggle())
        
        self.group_layout.addWidget(self.schedule_select)
        self.group_layout.addWidget(self.schedule_control)
        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)

        self.setLayout(self.main_layout)

    def toggle(self):
        if self.active:
            self.master.disable_schedule()
            self.schedule_control.setText("Start")
            self.schedule_select.setEnabled(True)
            self.active = False
        else:
            self.master.enable_schedule(self.schedule_select.currentText())
            self.schedule_control.setText("Stop")
            self.schedule_select.setEnabled(False)
            self.active = True
