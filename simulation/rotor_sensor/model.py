from line_protocol.protocol.transport import LineSerialSniffer
from line_protocol.protocol.virtual_bus import VirtualBus, SimulatedPeripheral
from line_protocol.network import load_network
from line_protocol.monitor.traffic import TrafficLogger
import logging

class RotorSensorSimulation(SimulatedPeripheral):
    pass


class RotorSensorPhysicalSimulation(SimulatedPeripheral):
    def __init__(self, node, weight, initial_speed, wheel_diameter, gears, initial_gear, chainring_teeth, max_cadence):
        super().__init__(node)

        self.weight = weight
        self.speed = initial_speed
        self.wheel_diameter = wheel_diameter
        self.gears = gears
        self.current_gear = initial_gear
        self.chainring_teeth = chainring_teeth
        self.max_cadence = max_cadence

        self.kinetic_energy = 1 / 2 * self.weight * self.speed ** 2  # Kinetic energy formula
        self.potential_energy = 0
        self.pedal_power = 0  # Power applied to the pedals
        self.brake_power = 0
        self.road_grade = 0  # Road grade (0% for flat, positive for uphill, negative for downhill)
        self.cadence = 0  # Pedal cadence (RPM)
    
    def on_tick(self, delta_time):
        self.kinetic_energy += self.pedal_power * delta_time
        self.kinetic_energy -= self.brake_power * delta_time
        self.kinetic_energy -= self.road_grade * self.weight * 9.81 * delta_time

        # TODO: limit potential change based on distance traveled
        potential_change = self.road_grade * self.weight * 9.81 * delta_time
        self.potential_energy += potential_change
        self.kinetic_energy -= potential_change

        self.kinetic_energy = max(0, self.kinetic_energy)  # Ensure kinetic energy is non-negative

        self.speed = (2 * self.kinetic_energy / self.weight) ** 0.5

class RotorSensorPhysicalSimulationPanel():
    pass
