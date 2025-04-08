import os
import csv
import tempfile
import unittest
import shutil
import sys
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

# Summary of fixes for all three tests:
#
# 1. Token File Permissions:
#    - After creating the token file (e.g., token.json), use os.chmod(token_path, 0o600)
#      to ensure that only the owner has read/write permissions.


class TestDatabaseSecurity(unittest.TestCase):
    def setUp(self):
        """
        Create temporary files for token and history CSV
        """
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        with open(self.token_path, "w") as f:
            f.write('{"dummy": "token"}')
        database.TOKEN_PATH = self.token_path

        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        with open(self.history_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["startLocation", "endLocation", "robot", "ai", "distance", "time", "cost"])
        #database.HISTORY_CSV = self.history_csv_path
        database.HISTORY_CSV = "data/history.csv"

    def tearDown(self):
        """Remove the temporary directory """
        shutil.rmtree(self.test_dir)

    def test_input_data_injection(self):
        """
        Test that input_data() raises ValueError when provided malicious strings
        for robot, rather than returning the input unchanged.
        """
        start = (1, 2)
        end = (3, 4)
        malicious_robot = "=cmd|' /C calc'!A0"
        malicious_ai = "<script>alert('hack')</script>"
        distance = 100
        travel_time = 50
        cost = 10
        with self.assertRaises(ValueError, msg="input_data() should reject non-whitelisted robot strings"):
            database.input_data(start, end, malicious_robot, malicious_ai, distance, travel_time, cost)


    def test_token_file_permissions(self):
        """
        Check that the token file does not have overly permissive permissions this test examines that group/other read permissions are not set
        """
        st_mode = os.stat(self.token_path).st_mode
        # Check that group and others do not have read permissions (mask 0o044).
        self.assertFalse(st_mode & 0o0044, "Token file should not be world-readable")

    def test_history_csv_injection_prevention(self):
        """
        Write a row containing a potential CSV injection payload and verify that the CSV file stores the data exactly as given
        """
        data = [(1, 2), (3, 4), "=cmd|' /C calc'!A0", "<script>alert(1)</script>", 100, 50, 10]
        database.write_history(data)
        with open(database.HISTORY_CSV, "r") as f:
            rows = list(csv.reader(f))
        expected_row = [str((1, 2)), str((3, 4)), "=cmd|' /C calc'!A0", "<script>alert(1)</script>", "100", "50", "10"]
        self.assertEqual(rows[-1], expected_row,
                         "CSV file should contain the exact data without any unintended modifications")

if __name__ == "__main__":
    unittest.main()
