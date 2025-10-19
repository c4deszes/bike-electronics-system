from line_protocol.protocol.simulation import SimulatedPeripheral

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

    def __init__(self, node):
        super().__init__(node)
        self.node = node
        self.listener = None

    def start(self):
        self.last_setpoint = 0

        # Diagnostics
        self.op_status = 'Ok'
        # TODO: implement power status

    def on_tick(self, delta):
        pass

    def set_brightness(self, brightness):
        if self.listener:
            self.listener.on_brightness_changed(brightness)

    def on_subscriber_event(self, request, signals):
        if request.name == 'LightSynchronization':
            self.set_brightness(signals['TargetBrightness'].phy)
        # TODO: handle rearlight setting
