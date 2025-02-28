import os
import csv
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

# Ensure the project root is in sys.path so we can import from the data folder.
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))

# Import the module under test.
import database

# (Optional) If your module uses hardcoded file paths, expose them as module-level variables:
# In database.py, you might set:
# TOKEN_PATH = "data/token.json"
# HISTORY_CSV = "data/history.csv"
#
# For testing, we override these paths:
database.TOKEN_PATH = None
database.HISTORY_CSV = None

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to simulate the data folder
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        
        # Create a dummy token file so authentication functions can work without real credentials.
        with open(self.token_path, "w") as token_file:
            token_file.write('{"dummy": "token"}')
        
        # Override the paths in the database module so that it uses our temporary files.
        database.TOKEN_PATH = self.token_path
        database.HISTORY_CSV = self.history_csv_path
        
        # Also create a dummy history.csv file if needed.
        with open(self.history_csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            # Write a header row as an example (or leave it empty)
            writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_input_data_valid(self):
        """Test that input_data returns a correctly formatted list for valid inputs."""
        data = database.input_data((32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
        expected = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        self.assertEqual(data, expected)

    def test_input_data_invalid(self):
        """Test that input_data raises ValueError for invalid startLocation."""
        with self.assertRaises(ValueError):
            database.input_data(("not a tuple", 232), (4323, 232), "robot1", "ai1", 120, 60, 1)

    @patch("database.build")
    def test_read_history_no_data(self, mock_build):
        """Test read_history returns an empty list when no data is found."""
        # Create a fake API response that returns no values.
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": []}
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, [])

    @patch("database.build")
    def test_read_history_with_data(self, mock_build):
        """Test read_history returns expected data when data exists."""
        fake_data = [["start", "end", "robot", "ai", "distance", "time", "cost"]]
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": fake_data}
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, fake_data)

    @patch("database.build")
    def test_write_history_to_cloud(self, mock_build):
        """Test that write_history_to_cloud calls the Sheets API update method."""
        # Write some dummy content to the CSV file.
        with open(self.history_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["dummy", "data", "robot1", "ai1", 100, 30, 50])

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        database.write_history_to_cloud("dummy_sheet_id", self.history_csv_path)
        self.assertTrue(mock_sheet.values.return_value.update.called)

    @patch("database.authenticate")
    @patch("database.build")
    def test_update_history(self, mock_build, mock_authenticate):
        """Test update_history clears and then updates the cloud sheet."""
        # Write dummy data into our history.csv.
        with open(self.history_csv_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])

        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        database.update_history()
        self.assertTrue(mock_sheet.values.return_value.clear.called)
        self.assertTrue(mock_sheet.values.return_value.update.called)

if __name__ == "__main__":
    unittest.main()
