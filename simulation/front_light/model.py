from line_protocol.protocol.virtual_bus import SimulatedPeripheral
import time

class FrontLightListener:

    def on_brightness_changed(self, brightness: int):
        """
        Called when the brightness of the front light changes.

        :param brightness: The new brightness level (0-100).
        """
        pass

class FrontLightSimulation(SimulatedPeripheral):
    """
    Simulates the Front Light of a vehicle.
    """

    def __init__(self, node):
        super().__init__(node)
        self.node = node
        self.listener: FrontLightListener

    def start(self):
        # Communication
        self.last_setpoint = 0

        # Diagnostics
        self.op_status = 'Ok'
        # TODO: implement power status

        # Control
        self.cycle_count = 0

        # Brightness control
        self.brightness = 0
        self.brightness_mode = 'off'

    def on_tick(self, delta):
        pass

    def press_button(self):
        self.cycle_count += 1
        if self.cycle_count >= 10:
            self.cycle_count = 0
        self.requests.FrontLightStatus.ControlCycleCount = self.cycle_count

    def set_brightness(self, brightness: int):
        if self.listener and brightness != self.brightness:
            self.listener.on_brightness_changed(brightness)
            self.brightness = brightness

    def on_subscriber_event(self, request, signals):
        if request.name == 'LightSynchronization':
            self.set_brightness(signals['TargetBrightness'])


