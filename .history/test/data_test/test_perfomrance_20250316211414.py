import os
import csv
import tempfile
import unittest
import shutil
import time
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

class TestDatabasePerformance(unittest.TestCase):
    def setUp(self):
        """
        Set up a temporary CSV file for performance testing of write_history().
        """
        self.test_dir = tempfile.mkdtemp()
        database.HISTORY_CSV = os.path.join(self.test_dir, "history.csv")
        with open(database.HISTORY_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["startLocation", "endLocation", "robot", "ai", "distance", "time", "cost"])


    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    @patch("database.write_history_to_cloud")
    def test_write_history_performance(self, mock_write_history_to_cloud):
        """
        Check that writing 1000 rows using write_history() completes in a timely manner.
        """
        start_time = time.time()
        with patch("database.open", new_callable=mock_open) as m_open:
            for i in range(1000):
                data = [(i, i+1), (i+2, i+3), f"robot{i}", f"ai{i}", i*10, i*5, i]
                database.write_history(data)
        duration = time.time() - start_time

        # Assert that writing 1000 rows takes less than 1 second.
        self.assertLess(duration, 1.0,
                        f"Performance issue: writing 1000 rows took {duration:.2f} seconds")


    @patch("database.read_history")
    def test_read_history_performance(self, mock_read_history_to_cloud):
        """
        Check that writing 1000 rows using read_history() completes in a timely manner
        """
        start_time = time.time()
        for i in range(1000):
            
            database.read_history()
        duration = time.time() - start_time
    
        self.assertLess(duration, 1.0,
                        f"Performance issue: reading 1000 rows took {duration:.2f} seconds")

    @patch("database.update_history")
    def test_update_history_performance(self, mock_update_history):
        """
        Check that updating 1000 rows using update_history() completes in a timely manner
        """
        # Populate test data
        with open(database.HISTORY_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            for i in range(1000):
                writer.writerow([(i, i+1), (i+2, i+3), f"robot{i}", f"ai{i}", i*10, i*5, i])

        
        start_time = time.time()
        for i in range(1000):
            new_data = [(i, i+1), (i+2, i+3), f"robot_updated{i}", f"ai_updated{i}", i*20, i*10, i]
            database.update_history(i, new_data) 
        
        duration = time.time() - start_time
        self.assertLess(duration, 1.0, f"Performance issue: updating 1000 rows took {duration:.2f} seconds")

if __name__ == "__main__":
    unittest.main()

