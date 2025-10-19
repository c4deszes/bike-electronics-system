from line_protocol.protocol.simulation import SimulatedPeripheral

class BodyComputerSimulation(SimulatedPeripheral):
    """
    Simulates the Body Computer of a vehicle.
    """

    def __init__(self, node):
        super().__init__(node)
        self.node = node

        self.light_profile = [
            # TargetBrightness, LightMode, FrontBehavior, RearBehavior
            (20, 'Adaptive', 'Solid', 'Solid'),
            (40, 'Adaptive', 'Solid', 'Solid'),
            (60, 'Adaptive', 'Solid', 'Solid'),
            (80, 'Adaptive', 'Solid', 'Solid'),
            (100, 'Adaptive', 'Solid', 'Solid'),
            (40, 'Adaptive', 'Solid', 'Blink'),
            (70, 'Adaptive', 'Solid', 'Blink'),
            (100, 'Adaptive', 'Solid', 'Blink'),
            (80, 'Adaptive', 'Blink', 'Blink'),
            (0, 'Adaptive', 'Solid', 'Solid'),
        ]

    def start(self):
        self.last_cycle_count = 0
        self.last_status = 'NotStarted'
        self.active = False

    def on_tick(self, delta):
        """
        Called on each tick of the simulation.
        :param delta: Time since last tick in seconds.
        """
        pass

    def on_subscriber_event(self, request, signals):
        if request.name == 'FrontLightStatus':
            new_cycle_count = signals['ControlCycleCount'].phy

            if new_cycle_count != self.last_cycle_count:
                self.active = True
                self.last_cycle_count = new_cycle_count

        if request.name == 'RideStatus':
            status = signals['RideStatus'].phy

            if status != self.last_status:
                if status == 'Active':
                    self.active = True
                elif status == 'Idle':
                    self.active = False
                self.last_status = status

        if not self.active:
            brightness = 20
        else:
            brightness = self.light_profile[self.last_cycle_count][0]

        self.requests.LightSynchronization.TargetBrightness = brightness
        self.requests.LightSynchronization.LightMode = self.light_profile[self.last_cycle_count][1]
        self.requests.FrontLightSetting.Behavior = self.light_profile[self.last_cycle_count][2]
        self.requests.RearLightSetting.Behavior = self.light_profile[self.last_cycle_count][3]
