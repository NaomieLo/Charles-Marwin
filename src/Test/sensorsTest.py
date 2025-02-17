import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sensors import Sensor
import transformations
import numpy as np
import rasterio.transform
import unittest

class sensorTest(unittest.TestCase):


    def setUp(self):
        # same map as Yijun
        self.mock_elevation_map = np.array([
            [10, 2, -3, 100, 1],
            [-1, 22000, -1, 3, 20],
            [400, -300, 0.0, -8250, 50],
            [300, -200, 3, -1, 55],
            [10, -10, 1, 1, 1]
        ]) 

        self.affine_transform = rasterio.transform.Affine(1, 0, 0, 0, -1, 0)
        #(row, col) -> (x, y)
        # x = col, y = -row

        self.sensor = Sensor(self.mock_elevation_map, self.affine_transform)

    def test_get_elevation_at_position(self):
        self.assertEqual(self.sensor.get_elevation_at_position(0, 0), None)
        self.assertEqual(self.sensor.get_elevation_at_position(1, 1), 22000)
        self.assertEqual(self.sensor.get_elevation_at_position(4, 4), 1)

    
    def test_get_elevation_out_of_bounds(self):
        """Test retrieval of elevation at out-of-bounds positions."""
        self.assertIsNone(self.sensor.get_elevation_at_position(-1, 0))  # Above grid
        self.assertIsNone(self.sensor.get_elevation_at_position(10, 10))  # Outside grid

    def test_handle_missing_elevation(self):
        """Test if the sensor estimates missing elevation correctly."""
        elevation = self.sensor.get_elevation_at_position(2, 2) 
        self.assertGreater(elevation, Sensor.MIN_ELEVATION)

    def test_is_passable(self): #CHECK: Assuming passable elevation is 100
        """Test if movement between points is correctly validated."""
        self.assertTrue(self.sensor.is_passable(3, 3, 4, 4))  
        self.assertFalse(self.sensor.is_passable(1, 1, 2, 2))  

    def test_get_cost(self):
        """Test movement cost between two points."""
        cost = self.sensor.get_cost(3, 3, 4, 4) 
        self.assertGreater(cost, 1.0)  # Should be at least base movement cost

    def test_get_neighbors(self):
        """Test if neighbor calculation works correctly."""
        neighbors = self.sensor.get_neighbors(2, 2)
        self.assertEqual(len(neighbors), 8)  # 8 neighbors for a valid cell

if __name__ == '__main__':
    unittest.main()


