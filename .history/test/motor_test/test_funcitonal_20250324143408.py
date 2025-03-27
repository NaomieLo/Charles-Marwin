import sys
import os
import time
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../../src"))
sys.path.insert(0, src_dir)

import sensors
from motors import Motors


# Dummy sensor
class DummySensor:
    @staticmethod
    def get_elevation_at_position():
        return 5  # Flat ground (0 <= elevation <= 10)


def test_consume_battery_flat():
    # Monkey-patch the sensor to return a flat ground elevation.
    sensors.Sensor = DummySensor

    motors = Motors(elevation_map=None, affine_transform=None)
    motors.battery = 100.0  # reset battery
    old_battery = motors.battery

    # When on flat ground, battery should be multiplied by FLATGROUND_POWER (0.99)
    result = motors.consume_battery()
    expected = old_battery * motors.FLATGROUND_POWER

    assert (
        abs(motors.battery - expected) < 0.001
    ), "Battery consumption on flat ground is incorrect"
    assert (
        result is True
    ), "consume_battery should return True when battery remains above 0"


def test_motor_start_stop():
    # Use dummy sensor; not used in start/stop but needed for class instantiation.
    sensors.Sensor = DummySensor

    motors = Motors(elevation_map=None, affine_transform=None)
    motors.battery = 50.0  # Ensure battery is not depleted

    # Start motors
    start_result = motors.start_motors()
    assert start_result is True, "Motors should start with sufficient battery"
    assert (
        motors.is_running is True
    ), "Motors is_running flag should be True after start"
    assert (
        motors.charging_thread is not None
    ), "Charging thread should be created after starting motors"

    # Allow the charging thread to run briefly
    time.sleep(2)

    # Stop motors
    motors.stop()
    assert motors.is_running is False, "Motors should not be running after stop"
    assert motors.is_stopped is True, "Motors is_stopped flag should be True after stop"


def test_charge_battery():
    # Test that the battery charges correctly when enough time has passed.
    sensors.Sensor = DummySensor
    motors = Motors(elevation_map=None, affine_transform=None)
    motors.battery = 80.0

    # Simulate that last action was long enough ago for charging to occur.
    motors.last_action_time = time.time() - 6

    # Capture battery before charging
    old_battery = motors.battery
    motors.charge_battery()

    # Expected battery: battery multiplied by CHARGING_RATE (1.02), capped at 100.
    expected = min(100.0, old_battery * motors.CHARGING_RATE)
    assert (
        abs(motors.battery - expected) < 0.001
    ), "Battery charging did not work as expected"


# The following block is optional when running with pytest.
if __name__ == "__main__":
    test_consume_battery_flat()
    test_motor_start_stop()
    test_charge_battery()
    print("Functional tests passed.")
