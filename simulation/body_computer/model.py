from line_protocol.protocol.virtual_bus import SimulatedPeripheral

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
        pass

    def on_tick(self, delta):
        """
        Called on each tick of the simulation.
        :param delta: Time since last tick in seconds.
        """
        pass

    def on_subscriber_event(self, request, signals):
        if request.name == 'FrontLightStatus':
            cycle_count = signals['ControlCycleCount']
            self.requests.LightSynchronization.TargetBrightness = self.light_profile[cycle_count][0]
            self.requests.LightSynchronization.LightMode = self.light_profile[cycle_count][1]
            self.requests.FrontLightSetting.Behavior = self.light_profile[cycle_count][2]
            self.requests.RearLightSetting.Behavior = self.light_profile[cycle_count][3]
