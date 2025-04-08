import os
import csv
import tempfile
import unittest
import shutil
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

class TestDatabaseFunctional(unittest.TestCase):
    def setUp(self):
        """
        Create a temporary directory for token and history CSV file testing.
        Override TOKEN_PATH and HISTORY_CSV in the database module.
        """
        self.test_dir = tempfile.mkdtemp()
        database.TOKEN_PATH = os.path.join(self.test_dir, "token.json")
        database.HISTORY_CSV = os.path.join(self.test_dir, "history.csv")
        
        # Create a dummy token file.
        with open(database.TOKEN_PATH, "w") as f:
            f.write('{"dummy": "token"}')
        
        # Create an empty CSV file with header.
        with open(database.HISTORY_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["startLocation", "endLocation", "robot", "ai", "distance", "time", "cost"])

    def tearDown(self):
        """Remove the temporary directory after each test."""
        shutil.rmtree(self.test_dir)

    def test_input_data_valid(self):
        """
        Verify that input_data() returns the expected list when valid parameters are provided.
        """
        start = (1, 2)
        end = (3, 4)
        robot = "robotX"
        ai = "aiX"
        distance = 100
        travel_time = 50
        cost = 10
        result = database.input_data(start, end, robot, ai, distance, travel_time, cost)
        expected = [start, end, robot, ai, distance, travel_time, cost]
        self.assertEqual(result, expected, "input_data() should return the correct ordered list.")

    def test_input_data_invalid(self):
        """
        Verify that input_data() raises a ValueError when an invalid startLocation is passed.
        """
        start = ("invalid", 2)
        end = (3, 4)
        robot = "robotX"
        ai = "aiX"
        distance = 100
        travel_time = 50
        cost = 10
        with self.assertRaises(ValueError):
            database.input_data(start, end, robot, ai, distance, travel_time, cost)

if __name__ == "__main__":
    unittest.main()
