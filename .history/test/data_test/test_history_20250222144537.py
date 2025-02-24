import os
import csv
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Adjust the import path to where your database.py is located.
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

# Even though write_history() uses hard-coded paths ("data/history.csv"),
# we still override TOKEN_PATH for authentication tests.
database.TOKEN_PATH = None
database.HISTORY_CSV = None

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        """
        Creates a temporary directory for tokens.
        Note: write_history() still writes to "data/history.csv",
        so we patch open() in that test instead of using a temp file.
        """
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        # Create a dummy token file in the temporary directory.
        with open(self.token_path, "w") as f:
            f.write('{"dummy": "token"}')
        
        # Override the token path in the module so authentication works.
        database.TOKEN_PATH = self.token_path
        
        # For tests that rely on local CSV content (like update_history),
        # we create a temporary history file and then patch open() to redirect calls.
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        with open(self.history_csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])

    def tearDown(self):
        """Removes the temporary directory after each test."""
        shutil.rmtree(self.test_dir)

    def test_input_data_valid(self):
        """
        Test that input_data() returns the correct list of values for valid inputs.
        """
        start = (32, 232)
        end = (4323, 232)
        robot = "robot1"
        ai = "ai1"
        distance = 120
        travel_time = 60
        cost = 1

        result = database.input_data(start, end, robot, ai, distance, travel_time, cost)
        expected = [start, end, robot, ai, distance, travel_time, cost]
        self.assertEqual(result, expected,
                         "input_data() should return a correctly ordered list of values.")

    def test_input_data_invalid(self):
        """
        Test that input_data() raises ValueError for invalid startLocation.
        """
        start = ("invalid", 232)
        end = (4323, 232)
        robot = "robot1"
        ai = "ai1"
        distance = 120
        travel_time = 60
        cost = 1

        with self.assertRaises(ValueError):
            database.input_data(start, end, robot, ai, distance, travel_time, cost)

    @patch("database.build")
    def test_read_history_no_data(self, mock_build):
        """
        Test read_history() returns an empty list if the Sheets API returns no values.
        """
        # Set up the mock Sheets API to return no data.
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": []}
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, [],
                         "read_history() should return an empty list if no data is found.")

    @patch("database.build")
    def test_read_history_with_data(self, mock_build):
        """
        Test read_history() returns a list of lists when the Sheets API provides data.
        """
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        fake_data = [
            ["start", "end", "robot", "ai", "distance", "time", "cost"],
            ["(1,2)", "(3,4)", "robot1", "ai1", "100", "50", "10"]
        ]
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": fake_data}
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, fake_data,
                         "read_history() should return exactly the data provided by the Sheets API.")

    @patch("database.write_history_to_cloud")
    @patch("database.open", new_callable=mock_open, read_data="start,end,robot,ai,distance,time,cost\n")
    def test_write_history(self, mock_file, mock_write_history_to_cloud):
        """
        Test write_history() writes data to the local CSV file and calls write_history_to_cloud().
        Since write_history() uses a hard-coded file path ("data/history.csv"),
        we patch open() in the database module to intercept file writes.
        """
        data = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        database.write_history(data)

        # Verify that open() was called with the correct file path and mode.
        mock_file.assert_called_with("data/history.csv", mode="a", newline="")

        # Verify that write_history_to_cloud was called with the expected arguments.
        mock_write_history_to_cloud.assert_called_once_with(database.sheet_id, "data/history.csv")

    @patch("database.authenticate")
    @patch("database.build")
    def test_update_history(self, mock_build, mock_authenticate):
        """
        Test that update_history() clears the remote sheet and then updates it
        with the local CSV data.
        """
        # Set up the mock authentication credentials.
        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds

        # Set up the mock Sheets API.
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        # Write an extra line to the local history CSV to simulate data.
        with open(self.history_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["(1,2)", "(3,4)", "robot1", "ai1", "120", "60", "1"])

        # Patch the open() call inside update_history() so that it reads from our temporary file.
        # We simulate the file's content by reading from our temporary file.
        with patch("database.open", new_callable=lambda: open(self.history_csv_path, "r")):
            database.update_history()

        # Assert that the clear() and update() methods were called on the remote sheet.
        mock_sheet.values.return_value.clear.assert_called_once()
        mock_sheet.values.return_value.update.assert_called_once()


if __name__ == "__main__":
    unittest.main()
