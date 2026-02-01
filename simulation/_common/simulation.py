
class SimulationMember:
    def start(self):
        raise NotImplementedError()
    
    def reset(self):
        raise NotImplementedError()
    
    def on_tick(self, delta: float):
        raise NotImplementedError()
