import os
import csv
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Assume your production code is in a file called history.py
import history

class TestHistoryFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for file I/O tests
        self.test_dir = tempfile.mkdtemp()
        # Override paths for token.json and history.csv to point into this temporary directory
        self.token_path = os.path.join(self.test_dir, "token.json")
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        # Write a dummy token file so that authentication functions don’t fail
        with open(self.token_path, "w") as token_file:
            token_file.write('{"dummy": "token"}')
        # Monkey-patch file paths in the module (if you can, refactor the module to accept paths)
        history.TOKEN_PATH = self.token_path  # If you decide to parameterize token file path
        history.HISTORY_CSV = self.history_csv_path

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_input_data_valid(self):
        # Test valid input
        data = history.input_data((32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
        expected = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        self.assertEqual(data, expected)

    def test_input_data_invalid_start_location(self):
        # Test invalid start location
        with self.assertRaises(ValueError):
            history.input_data(("invalid", 232), (4323, 232), "robot1", "ai1", 120, 60, 1)

    @patch("history.build")
    def test_read_history_no_data(self, mock_build):
        # Simulate an empty sheet response
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        # Create a fake response with no values
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": []}
        mock_build.return_value = mock_service

        result = history.read_history()
        self.assertEqual(result, [])

    @patch("history.build")
    def test_write_history_to_cloud(self, mock_build):
        # Create a dummy CSV file in our temporary directory
        with open(self.history_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["col1", "col2"])

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        # Call write_history_to_cloud
        history.write_history_to_cloud("dummy_sheet_id", self.history_csv_path)
        # Verify that update was called
        self.assertTrue(mock_sheet.values.return_value.update.called)

    @patch("history.authenticate")
    @patch("history.build")
    def test_update_history(self, mock_build, mock_authenticate):
        # Write some dummy data into the local CSV file
        with open(self.history_csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["col1", "col2"])
        
        # Set up mocks for google sheet API calls
        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        # Call update_history which should read from local CSV and update the cloud sheet
        history.update_history()

        # Check that the clear and update methods were called
        self.assertTrue(mock_sheet.values.return_value.clear.called)
        self.assertTrue(mock_sheet.values.return_value.update.called)

if __name__ == "__main__":
    unittest.main()
