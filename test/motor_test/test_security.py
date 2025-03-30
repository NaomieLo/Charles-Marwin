import time
import os
import sys
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../../src"))
sys.path.insert(0, src_dir)

import sensors
from motors import Motors


# Dummy sensor
class DummySensor:
    @staticmethod
    def get_elevation_at_position():
        return 60  # Use a value in the "steep uphill" range (50 < elevation <= 100)


def test_battery_bounds():
    sensors.Sensor = DummySensor
    motors = Motors(elevation_map=None, affine_transform=None)

    # Test lower bound: battery should not be negative
    motors.battery = 1.0
    # Force consumption until it would go below 0
    for _ in range(10):
        motors.consume_battery()
    assert motors.battery >= 0, "Battery level dropped below 0!"

    # Test upper bound: charging should not exceed 100%
    motors.battery = 99.0
    motors.last_action_time = time.time() - 6  # simulate time passage for charging
    motors.charge_battery()
    assert motors.battery <= 100, "Battery level exceeded 100%!"


def test_invalid_battery_state():
    sensors.Sensor = DummySensor
    motors = Motors(elevation_map=None, affine_transform=None)

    # Set an invalid battery state (simulate a potential attack or bug)
    motors.battery = -10.0
    result = motors.consume_battery()
    # Expect consume_battery to warn and return False
    assert (
        result is False
    ), "consume_battery should return False when battery is already depleted"


if __name__ == "__main__":
    test_battery_bounds()
    test_invalid_battery_state()
    print("Security tests passed.")
