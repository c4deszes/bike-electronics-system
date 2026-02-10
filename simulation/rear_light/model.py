import time
from line_protocol.protocol.simulation import SimulatedPeripheral
from line_uds.profile import UdsProfile
from line_uds.simulation import SimulatedUdsExtension

class RearLightListener:

    def on_brightness_changed(self, brightness):
        """
        Called when the brightness of the rear light changes.
        :param brightness: The new brightness level.
        """
        pass

class RearLightSimulation(SimulatedPeripheral):
    """
    Simulates the Rear Light of a vehicle.
    """

    def __init__(self, node, uds_profile: UdsProfile):
        super().__init__(node)
        self.node = node
        self.uds_profile = uds_profile
        self.uds_extension = SimulatedUdsExtension(uds_profile)
        self.add_extension(self.uds_extension)
        self.listener = None

    def start(self):
        self.reset()

    def reset(self):
        self._power = 'off'
        self._brightness = 0

        self._blink_state = True
        self._blink_timer = self.uds_extension.properties[0x4050] / 1000

        self.last_setpoint = time.time()
        self.target_mode = 'Default'
        self.target_brightness = 0

        self.set_brightness(0)

    def on_tick(self, delta):
        current_time = time.time()

        if current_time - self.last_setpoint > 4:
            self.target_brightness = 80
            self.target_mode = 'Default'

        if self.target_mode == 'Blink':
            self._blink_timer -= delta
            if self._blink_timer <= 0:
                self._blink_state = not self._blink_state
                if self._blink_state:
                    self._blink_timer = self.uds_extension.properties[0x4050] / 1000
                else:
                    self._blink_timer = self.uds_extension.properties[0x4051] / 1000

            if self._blink_state:
                self.set_brightness(self.target_brightness)
            else:
                self.set_brightness(0)
        else:
            self.set_brightness(self.target_brightness)

    def set_brightness(self, brightness):
        if brightness != self._brightness:
            self._brightness = brightness
            if self.listener:
                self.listener.on_brightness_changed(brightness)

    def on_subscriber_event(self, request, signals):
        if request.name == 'LightSynchronization':
            self.last_setpoint = time.time()
            self.target_brightness = signals['TargetBrightness'].phy
        if request.name == 'RearLightSetting':
            self.last_setpoint = time.time()
            self.target_mode = signals['Behavior'].phy
