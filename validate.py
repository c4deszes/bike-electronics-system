from line_protocol.network import load_network
from line_uds.loader import load_profile

if __name__ == "__main__":
    # Load the network configuration from a JSON file
    try:
        load_network('network.json')
    except Exception as e:
        print(f"Error loading network configuration: {e}")

    # Validate UDS profiles
    try:
        load_profile('uds/front_light.json')
    except Exception as e:
        print(f"Error loading UDS profile: {e}")

    try:
        load_profile('uds/rear_light.json')
    except Exception as e:
        print(f"Error loading UDS profile: {e}")

    try:
        load_profile('uds/rotor_sensor.json')
    except Exception as e:
        print(f"Error loading UDS profile: {e}")
