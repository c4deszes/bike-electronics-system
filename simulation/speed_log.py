from line_protocol.protocol.master import LineMaster, RequestListener, Request, SignalValueContainer
from line_protocol.protocol.simulation import SimulatedPeripheral
from line_protocol.protocol.transport import LineSerialTransport
from line_protocol.network import load_network, Network

import time
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    network = load_network("network.json")
    transport = LineSerialTransport('/dev/ttyFTDI_B', network.baudrate)
    master = LineMaster(transport, network)

    class Xd(RequestListener):
        def __init__(self):
            super().__init__()

            self.global_speed = 0.0
            self.front_period = 0
            self.rear_period = 0

        def on_user_request(self, timestamp: float, request: Request, buffer: list[int], signals: SignalValueContainer) -> None:
            if request.name == 'SpeedStatus':
                self.global_speed = signals['Speed'].phy

            if request.name == 'RotorSensorSpeedDebug':
                self.front_period = signals['FrontSpeed'].raw
                self.rear_period = signals['RearSpeed'].raw

            period = self.front_period
            logging.info("Raw: %s, Period (ms): %s, Speed: %s", period, period / 10, self.global_speed)

        def on_error(self, timestamp: float, request: Request, error_type):
            pass 

    with transport:
        with master:
            master.add_request_listener(Xd())
            master.enable_schedule('RotorSensorSchedule')

            while True:
                try:
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    break

            master.disable_schedule()