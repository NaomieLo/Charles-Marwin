import os
import csv
import tempfile
import shutil
import unittest
import pytest
from unittest.mock import patch, MagicMock

# Import your production code
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))

# Now, import database.py
import database



# Override paths if your module supports it.
# For these examples, assume your history.py uses these module variables:
# TOKEN_PATH = "data/token.json"
# HISTORY_CSV = "data/history.csv"
# You can change them in your tests:
history.TOKEN_PATH = None  # We override in our tests
history.HISTORY_CSV = None

# -------------------------------
# Pytest & Unittest Test Cases
# -------------------------------

class TestHistoryFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for file I/O tests
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        # Write a dummy token file so that authentication functions do not fail
        with open(self.token_path, "w") as token_file:
            token_file.write('{"dummy": "token"}')
        # Monkey-patch the paths in the history module
        history.TOKEN_PATH = self.token_path
        history.HISTORY_CSV = self.history_csv_path

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_input_data_valid(self):
        # Valid input returns the correct data list
        data = history.input_data((32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
        expected = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        self.assertEqual(data, expected)

    def test_input_data_invalid_start_location(self):
        # Should raise ValueError when startLocation is invalid
        with self.assertRaises(ValueError):
            history.input_data(("invalid", 232), (4323, 232), "robot1", "ai1", 120, 60, 1)

    @patch("history.build")
    def test_read_history_no_data(self, mock_build):
        # Simulate a Google Sheets API response with no data
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        fake_response = {"values": []}
        mock_sheet.values.return_value.get.return_value.execute.return_value = fake_response
        mock_build.return_value = mock_service

        result = history.read_history()
        self.assertEqual(result, [])

    @patch("history.build")
    def test_write_history_to_cloud(self, mock_build):
        # Write a dummy CSV file and verify that update is called on the API
        with open(self.history_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["col1", "col2"])

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        history.write_history_to_cloud("dummy_sheet_id", self.history_csv_path)
        self.assertTrue(mock_sheet.values.return_value.update.called)

    @patch("history.authenticate")
    @patch("history.build")
    def test_update_history(self, mock_build, mock_authenticate):
        # Write dummy data into local CSV, then verify that the sheet update methods are called
        with open(self.history_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["col1", "col2"])
        
        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        history.update_history()

        self.assertTrue(mock_sheet.values.return_value.clear.called)
        self.assertTrue(mock_sheet.values.return_value.update.called)

# Pytest-style test function (optional)
def test_pytest_input_data_valid():
    data = history.input_data((32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
    expected = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
    assert data == expected

if __name__ == "__main__":
    unittest.main()
