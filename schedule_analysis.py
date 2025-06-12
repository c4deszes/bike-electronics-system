import logging
import pprint

from line_protocol.network import load_network
from line_protocol.util.schedule_analyze import analyze_schedule

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    network = load_network("network.json")
    result = analyze_schedule(network, network.get_schedule("NormalSchedule"), 10000)
    pprint.pprint(result)
