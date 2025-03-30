# test_performance.py
import time
import sensors
from Motors import Motors

# Dummy sensor for performance tests.
class DummySensor:
    @staticmethod
    def get_elevation_at_position():
        return 20  # any value for performance testing

def test_charge_battery_performance():
    sensors.Sensor = DummySensor
    motors = Motors(elevation_map=None, affine_transform=None)
    motors.battery = 50.0
    motors.last_action_time = time.time() - 6  # ensure charging condition met

    start_time = time.perf_counter()
    motors.charge_battery()
    duration = time.perf_counter() - start_time

    # Check that charging is performant (should take less than, say, 0.01 sec)
    assert duration < 0.01, f"charge_battery took too long: {duration:.4f} seconds"

def test_consume_battery_performance():
    sensors.Sensor = DummySensor
    motors = Motors(elevation_map=None, affine_transform=None)
    motors.battery = 100.0

    start_time = time.perf_counter()
    motors.consume_battery()
    duration = time.perf_counter() - start_time

    # Check that battery consumption is also fast (less than 0.01 sec)
    assert duration < 0.01, f"consume_battery took too long: {duration:.4f} seconds"

if __name__ == "__main__":
    test_charge_battery_performance()
    test_consume_battery_performance()
    print("Performance tests passed.")
