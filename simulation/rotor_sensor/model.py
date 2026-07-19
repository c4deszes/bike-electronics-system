import math
from line_protocol.protocol.simulation import SimulatedPeripheral

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

class RotorSensorSimulation(SimulatedPeripheral):
    """
    Rotor sensor simulator with a lightweight bike dynamics model.
    """

    def __init__(self, node):
        super().__init__(node)
        self.node = node
        self.start()

    def start(self):
        self.elapsed_time_s = 0.0
        self.distance_m = 0.0
        self.altitude_m = 0.0
        self.elevation_m = 0.0
        self.descent_m = 0.0

        self.speed_kmh = 18.0
        self.commanded_speed_kmh = self.speed_kmh
        self.top_speed_kmh = self.speed_kmh
        self.average_speed_kmh = self.speed_kmh

        self.road_grade_pct = 0.0
        self.brake_enabled = False
        self.brake_level = 0.0
        self.auto_brake_signal = True
        self.brake_signal_accel_threshold_mps2 = -0.8
        self.longitudinal_accel_mps2 = 0.0
        self.brake_signal_active = False

        self.wheel_diameter_m = 0.70
        self.wheel_angle_deg = 0.0

        self._update_request_signals()

    def set_speed_signal(self, speed_kmh: float):
        self.commanded_speed_kmh = max(0.0, float(speed_kmh))

    def set_road_grade(self, grade_pct: float):
        self.road_grade_pct = max(-20.0, min(20.0, float(grade_pct)))

    def set_braking(self, enabled: bool, level: float = 1.0):
        self.brake_enabled = bool(enabled)
        self.brake_level = max(0.0, min(1.0, float(level))) if enabled else 0.0

    def set_auto_brake_signal(self, enabled: bool):
        self.auto_brake_signal = bool(enabled)

    def set_brake_signal_accel_threshold(self, threshold_mps2: float):
        self.brake_signal_accel_threshold_mps2 = min(0.0, float(threshold_mps2))

    def on_tick(self, delta):
        delta = max(0.0, float(delta))
        if delta == 0.0:
            return

        self.elapsed_time_s += delta

        # Drive speed follows a command, then road grade and braking alter the net acceleration.
        follow_accel_kmh_s = (self.commanded_speed_kmh - self.speed_kmh) * 0.8
        grade_angle = math.atan(self.road_grade_pct / 100.0)
        grade_accel_kmh_s = -9.81 * math.sin(grade_angle) * 3.6
        brake_accel_kmh_s = -9.0 * self.brake_level if self.brake_enabled else 0.0

        prev_speed_kmh = self.speed_kmh
        self.speed_kmh += (follow_accel_kmh_s + grade_accel_kmh_s + brake_accel_kmh_s) * delta
        self.speed_kmh = max(0.0, self.speed_kmh)
        self.longitudinal_accel_mps2 = ((self.speed_kmh - prev_speed_kmh) / 3.6) / delta

        if self.auto_brake_signal:
            self.brake_signal_active = self.longitudinal_accel_mps2 <= self.brake_signal_accel_threshold_mps2
        else:
            self.brake_signal_active = self.brake_enabled and self.brake_level > 0

        speed_mps = self.speed_kmh / 3.6
        self.distance_m += speed_mps * delta

        altitude_step = speed_mps * math.sin(grade_angle) * delta
        self.altitude_m += altitude_step
        if altitude_step >= 0:
            self.elevation_m += altitude_step
        else:
            self.descent_m += abs(altitude_step)

        wheel_radius = max(0.1, self.wheel_diameter_m / 2.0)
        self.wheel_angle_deg = (self.wheel_angle_deg + math.degrees((speed_mps / wheel_radius) * delta)) % 360.0

        self.top_speed_kmh = max(self.top_speed_kmh, self.speed_kmh)
        self.average_speed_kmh = self.distance_m / self.elapsed_time_s * 3.6

        self._update_request_signals()

    def _update_request_signals(self):
        brake_state = 'Braking' if self.brake_signal_active else 'NotBraking'
        ride_status = 'Active' if self.speed_kmh > 0.5 else 'Idle'
        cadence = int(min(140, self.speed_kmh * 2.5))

        self.requests.SpeedStatus.Speed = self.speed_kmh
        self.requests.SpeedStatus.SpeedState = 'Ok'
        self.requests.SpeedStatus.BrakeState = brake_state
        self.requests.SpeedStatus.FrontWheelSlip = 'NotSlipping'
        self.requests.SpeedStatus.FrontWheelLockup = 'NoLockup'
        self.requests.SpeedStatus.RearWheelSlip = 'NotSlipping'
        self.requests.SpeedStatus.RearWheelLockup = 'NoLockup'

        self.requests.DrivetrainStatus.Cadence = cadence
        self.requests.DrivetrainStatus.CadenceStatus = 'Ok' if cadence > 0 else 'Coasting'
        self.requests.DrivetrainStatus.EstimatedGear = 3
        self.requests.DrivetrainStatus.GearStatus = 'Ok'

        self.requests.RideStatus.Duration = int(self.elapsed_time_s)
        self.requests.RideStatus.RideStatus = ride_status
        self.requests.RideStatus.DistanceStatus = 'Ok'
        self.requests.RideStatus.Distance = int(self.distance_m)

        self.requests.RoadStatus.Altitude = int(self.altitude_m)
        self.requests.RoadStatus.Grade = int(round(self.road_grade_pct))
        self.requests.RoadStatus.RoadQuality = 'Flat'
        self.requests.RoadStatus.ITPMS = 'Running' if self.speed_kmh > 0.5 else 'Stopped'
        self.requests.RoadStatus.PressureError = 'Ok'
        self.requests.RoadStatus.TemperatureError = 'Ok'
        self.requests.RoadStatus.AltitudeError = 'Ok'

        self.requests.RideStatistics.TopSpeed = self.top_speed_kmh
        self.requests.RideStatistics.AverageSpeed = self.average_speed_kmh
        self.requests.RideStatistics.Elevation = int(self.elevation_m)
        self.requests.RideStatistics.Descent = int(self.descent_m)


class _BikeRoadCanvas(QWidget):
    def __init__(self, simulation: RotorSensorSimulation, parent=None):
        super().__init__(parent)
        self.simulation = simulation
        self.setMinimumSize(420, 220)

    def _draw_wheel(self, painter: QPainter, x: float, y: float, radius: float, spoke_angle_deg: float):
        painter.setPen(QPen(QColor(40, 40, 40), 2))
        painter.setBrush(QColor(245, 245, 245))
        painter.drawEllipse(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))

        for base_deg in (0, 60, 120):
            ang = math.radians(base_deg + spoke_angle_deg)
            dx = math.cos(ang) * radius * 0.9
            dy = math.sin(ang) * radius * 0.9
            painter.drawLine(int(x - dx), int(y - dy), int(x + dx), int(y + dy))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor(230, 244, 255))

        w = self.width()
        h = self.height()

        grade_angle = math.atan(self.simulation.road_grade_pct / 100.0)
        t_x = math.cos(grade_angle)
        t_y = -math.sin(grade_angle)
        n_x = -math.sin(grade_angle)
        n_y = -math.cos(grade_angle)

        ground_center_x = w * 0.5
        ground_center_y = h * 0.72

        p1_x = ground_center_x - t_x * w
        p1_y = ground_center_y - t_y * w
        p2_x = ground_center_x + t_x * w
        p2_y = ground_center_y + t_y * w

        painter.setPen(QPen(QColor(60, 120, 60), 7))
        painter.drawLine(int(p1_x), int(p1_y), int(p2_x), int(p2_y))

        wheel_r = min(w, h) * 0.12
        wheel_spacing = wheel_r * 3.2

        rear_contact_x = ground_center_x - t_x * (wheel_spacing / 2)
        rear_contact_y = ground_center_y - t_y * (wheel_spacing / 2)
        front_contact_x = ground_center_x + t_x * (wheel_spacing / 2)
        front_contact_y = ground_center_y + t_y * (wheel_spacing / 2)

        rear_center_x = rear_contact_x + n_x * wheel_r
        rear_center_y = rear_contact_y + n_y * wheel_r
        front_center_x = front_contact_x + n_x * wheel_r
        front_center_y = front_contact_y + n_y * wheel_r

        self._draw_wheel(painter, rear_center_x, rear_center_y, wheel_r, self.simulation.wheel_angle_deg)
        self._draw_wheel(painter, front_center_x, front_center_y, wheel_r, self.simulation.wheel_angle_deg)

        frame_pen = QPen(QColor(30, 80, 130), 4)
        painter.setPen(frame_pen)

        bb_x = (rear_center_x + front_center_x) / 2
        bb_y = (rear_center_y + front_center_y) / 2 - wheel_r * 0.6

        seat_x = rear_center_x + t_x * wheel_r * 0.8 + n_x * wheel_r * 1.2
        seat_y = rear_center_y + t_y * wheel_r * 0.8 + n_y * wheel_r * 1.2
        handle_x = front_center_x - t_x * wheel_r * 0.5 + n_x * wheel_r * 1.2
        handle_y = front_center_y - t_y * wheel_r * 0.5 + n_y * wheel_r * 1.2

        painter.drawLine(int(rear_center_x), int(rear_center_y), int(bb_x), int(bb_y))
        painter.drawLine(int(bb_x), int(bb_y), int(front_center_x), int(front_center_y))
        painter.drawLine(int(rear_center_x), int(rear_center_y), int(seat_x), int(seat_y))
        painter.drawLine(int(seat_x), int(seat_y), int(handle_x), int(handle_y))
        painter.drawLine(int(handle_x), int(handle_y), int(front_center_x), int(front_center_y))

        painter.setPen(QPen(QColor(20, 20, 20), 2))
        painter.setBrush(QColor(20, 20, 20))
        painter.drawEllipse(int(bb_x - 8), int(bb_y - 8), 16, 16)


class RotorSensorSimulationPanel(QWidget):
    def __init__(self, simulation: RotorSensorSimulation, parent=None):
        super().__init__(parent)
        self.simulation = simulation

        self.main_layout = QHBoxLayout()
        self.group = QGroupBox("Rotor Sensor Bike Simulation")
        self.group_layout = QVBoxLayout()

        self.canvas = _BikeRoadCanvas(self.simulation)
        self.group_layout.addWidget(self.canvas)

        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.0, 80.0)
        self.speed_spin.setSingleStep(0.5)
        self.speed_spin.setSuffix(" km/h")
        self.speed_spin.setValue(self.simulation.commanded_speed_kmh)
        self.speed_spin.valueChanged.connect(self.simulation.set_speed_signal)

        self.grade_spin = QDoubleSpinBox()
        self.grade_spin.setRange(-20.0, 20.0)
        self.grade_spin.setSingleStep(0.5)
        self.grade_spin.setSuffix(" %")
        self.grade_spin.setValue(self.simulation.road_grade_pct)
        self.grade_spin.valueChanged.connect(self.simulation.set_road_grade)

        self.brake_checkbox = QCheckBox("Braking")
        self.brake_checkbox.stateChanged.connect(
            lambda state: self.simulation.set_braking(state != 0, 1.0)
        )

        self.auto_brake_checkbox = QCheckBox("Auto brake signal from acceleration")
        self.auto_brake_checkbox.setChecked(self.simulation.auto_brake_signal)
        self.auto_brake_checkbox.stateChanged.connect(
            lambda state: self.simulation.set_auto_brake_signal(state != 0)
        )

        self.brake_threshold_spin = QDoubleSpinBox()
        self.brake_threshold_spin.setRange(-5.0, 0.0)
        self.brake_threshold_spin.setSingleStep(0.1)
        self.brake_threshold_spin.setSuffix(" m/s^2")
        self.brake_threshold_spin.setValue(self.simulation.brake_signal_accel_threshold_mps2)
        self.brake_threshold_spin.valueChanged.connect(
            self.simulation.set_brake_signal_accel_threshold
        )

        self.current_speed_label = QLabel("Current speed: 0.0 km/h")
        self.current_grade_label = QLabel("Road grade: 0.0 %")
        self.current_accel_label = QLabel("Acceleration: 0.00 m/s^2")
        self.current_brake_signal_label = QLabel("Brake signal: NotBraking")

        control_form = QFormLayout()
        control_form.addRow("Speed setpoint", self.speed_spin)
        control_form.addRow("Road grade", self.grade_spin)
        control_form.addRow("Brake", self.brake_checkbox)
        control_form.addRow("Auto brake signal", self.auto_brake_checkbox)
        control_form.addRow("Brake accel threshold", self.brake_threshold_spin)

        control_box = QWidget()
        control_box.setLayout(control_form)
        self.group_layout.addWidget(control_box)
        self.group_layout.addWidget(self.current_speed_label)
        self.group_layout.addWidget(self.current_grade_label)
        self.group_layout.addWidget(self.current_accel_label)
        self.group_layout.addWidget(self.current_brake_signal_label)

        self.group.setLayout(self.group_layout)
        self.main_layout.addWidget(self.group)
        self.setLayout(self.main_layout)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_view)
        self.refresh_timer.start(33)

    def _refresh_view(self):
        self.current_speed_label.setText(f"Current speed: {self.simulation.speed_kmh:.1f} km/h")
        self.current_grade_label.setText(f"Road grade: {self.simulation.road_grade_pct:.1f} %")
        self.current_accel_label.setText(f"Acceleration: {self.simulation.longitudinal_accel_mps2:.2f} m/s^2")
        state = 'Braking' if self.simulation.brake_signal_active else 'NotBraking'
        self.current_brake_signal_label.setText(f"Brake signal: {state}")
        self.canvas.update()

