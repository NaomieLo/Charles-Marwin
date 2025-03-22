# import os
# import csv
# import tempfile
# import unittest
# import shutil
# import time
# import sys
# from unittest.mock import patch

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
# import database

# class TestDatabasePerformance(unittest.TestCase):
#     def setUp(self):
#         """
#         Set up a temporary CSV file for performance testing of write_history().
#         """
#         self.test_dir = tempfile.mkdtemp()
#         database.HISTORY_CSV = os.path.join(self.test_dir, "history.csv")
#         with open(database.HISTORY_CSV, "w", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow(["startLocation", "endLocation", "robot", "ai", "distance", "time", "cost"])


#     def tearDown(self):
#         """Clean up the temporary directory."""
#         shutil.rmtree(self.test_dir)

#     @patch("database.write_history_to_cloud")
#     def test_write_history_performance(self, mock_write_history_to_cloud):
#         """
#         Check that writing 1000 rows using write_history() completes in a timely manner
#         """
#         start_time = time.time()
#         for i in range(1000):
#             data = [(i, i+1), (i+2, i+3), f"robot{i}", f"ai{i}", i*10, i*5, i]
#             database.write_history(data)
#         duration = time.time() - start_time
        
#         # Assert that writing 1000 rows takes less than 1 second.
#         self.assertLess(duration, 1.0,
#                         f"Performance issue: writing 1000 rows took {duration:.2f} seconds")

#     @patch("database.read_history")
#     def test_read_history_performance(self, mock_read_history_to_cloud):
#         """
#         Check that writing 1000 rows using read_history() completes in a timely manner
#         """
#         start_time = time.time()
#         for i in range(1000):
            
#             database.read_history()
#         duration = time.time() - start_time
    
#         self.assertLess(duration, 1.0,
#                         f"Performance issue: reading 1000 rows took {duration:.2f} seconds")

#     @patch("database.update_history")
#     def test_update_history_performance(self, mock_update_history):
#         """
#         Check that updating 1000 rows using update_history() completes in a timely manner
#         """
#         # Populate test data
#         with open(database.HISTORY_CSV, "a", newline="") as f:
#             writer = csv.writer(f)
#             for i in range(1000):
#                 writer.writerow([(i, i+1), (i+2, i+3), f"robot{i}", f"ai{i}", i*10, i*5, i])

        
#         start_time = time.time()
#         for i in range(1000):
#             new_data = [(i, i+1), (i+2, i+3), f"robot_updated{i}", f"ai_updated{i}", i*20, i*10, i]
#             database.update_history(i, new_data) 
        
#         duration = time.time() - start_time
#         self.assertLess(duration, 1.0, f"Performance issue: updating 1000 rows took {duration:.2f} seconds")

# if __name__ == "__main__":
#     unittest.main()


import os
import csv
import tempfile
import unittest
import shutil
import time
import sys
from unittest.mock import patch, MagicMock, mock_open
import builtins

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

class TestDatabasePerformance(unittest.TestCase):

    def setUp(self):
        """
        Creates a temporary directory for token and history file testing.
        The token file is created in a temp directory, and we create a
        temporary CSV file to simulate local history data.
        """
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        with open(self.token_path, "w") as f:
            f.write('{"dummy": "token"}')
        database.TOKEN_PATH = self.token_path

        # Create a temporary history CSV file
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        with open(self.history_csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["startLocation", "endLocation", "robot", "ai", "distance", "time", "cost"])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 122])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1220])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1])
        # Point the module-level variable to our temporary file.
        database.HISTORY_CSV = self.history_csv_path

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    @patch("database.write_history_to_cloud")
    def test_write_history_performance(self, mock_write_history_to_cloud):
        """
        Check that writing 1000 rows using write_history() completes in a timely manner.
        """
        start_time = time.time()
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
        Check that reading history using read_history() completes in a timely manner.
        """
        start_time = time.time()
        for i in range(1000):
            database.read_history()
        duration = time.time() - start_time
    
        self.assertLess(duration, 1.0,
                        f"Performance issue: reading 1000 rows took {duration:.2f} seconds")

    def test_update_history_performance(self):
        """
        Check that updating 1000 rows using update_history() completes in a timely manner.
        This test uses the actual update_history() function (without patching it) so that
        performance is measured on the real implementation.
        """
        # Populate the temporary history CSV with 1000 additional rows.
        with open(database.HISTORY_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            for i in range(1000):
                writer.writerow([(i, i+1), (i+2, i+3), f"robot{i}", f"ai{i}", i*10, i*5, i])
    
        # Patch builtins.open so that any call to open("data/history.csv", ...) is redirected to our temporary file.
        original_open = builtins.open

        def custom_open(file, mode='r', *args, **kwargs):
            if file == "data/history.csv":
                return original_open(self.history_csv_path, mode, *args, **kwargs)
            return original_open(file, mode, *args, **kwargs)
    
        with patch("builtins.open", side_effect=custom_open):
            start_time = time.time()
            # Call update_history() once (without parameters) since update_history() takes no arguments.
            database.update_history()
            duration = time.time() - start_time

        self.assertLess(duration, 1.0,
                        f"Performance issue: updating 1000 rows took {duration:.2f} seconds")

if __name__ == "__main__":
    unittest.main()
