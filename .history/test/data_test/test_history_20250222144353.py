import os
import csv
import tempfile
import shutil
import unittest

from unittest.mock import patch, MagicMock
from googleapiclient.errors import HttpError

# Adjust the import path to wherever your database.py is located:
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

# The main test class
class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        """
        Creates a temporary directory and CSV file for tests,
        and overrides database paths with these test paths.
        """
        self.test_dir = tempfile.mkdtemp()
        # Create dummy token path
        self.token_path = os.path.join(self.test_dir, "token.json")
        # Create a temporary history.csv path
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")

        # Write a dummy token file
        with open(self.token_path, "w") as f:
            f.write('{"dummy": "token"}')
        
        # Overwrite the paths in our database module so it doesn't use real ones
        database.TOKEN_PATH = self.token_path
        database.HISTORY_CSV = self.history_csv_path

        # Create a dummy CSV file with just a header
        with open(self.history_csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])

    def tearDown(self):
        """Removes the temporary directory after each test."""
        shutil.rmtree(self.test_dir)

    def test_input_data_valid(self):
        """
        Test that input_data returns the correct list of values for valid inputs.
        """
        # Given valid data:
        start = (32, 232)
        end = (4323, 232)
        robot = "robot1"
        ai = "ai1"
        distance = 120
        travel_time = 60
        cost = 1

        # When we call input_data
        result = database.input_data(start, end, robot, ai, distance, travel_time, cost)
        
        # Then the result should match the format
        expected = [start, end, robot, ai, distance, travel_time, cost]
        self.assertEqual(result, expected, "input_data should return a correctly ordered list of values.")

    def test_input_data_invalid(self):
        """
        Test that input_data raises ValueError for invalid startLocation parameter.
        """
        # invalid start location: first element is a string
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
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        # Return an empty list from the cloud
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": []}
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, [], "read_history should return an empty list if no data found.")

    @patch("database.build")
    def test_read_history_with_data(self, mock_build):
        """
        Test read_history() returns a list of lists if the Sheets API has data.
        """
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        # Return some dummy data
        fake_data = [["start", "end", "robot", "ai", "distance", "time", "cost"],
                     ["(1,2)", "(3,4)", "robot1", "ai1", "100", "50", "10"]]
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": fake_data}
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(
            result, 
            fake_data, 
            "read_history should return the data from the Sheets API exactly."
        )

    @patch("database.build")
    def test_write_history(self, mock_build):
        """
        Test that write_history(data) writes to the local CSV 
        and calls write_history_to_cloud() which updates the cloud.
        """
        # For mocking the final call inside write_history -> write_history_to_cloud()
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        # The data to be written
        data = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]

        # Call write_history from database
        database.write_history(data)

        # Check that the data was appended to the local CSV
        with open(self.history_csv_path, "r") as f:
            rows = list(csv.reader(f))
        # We had 1 header row + 1 row of data
        self.assertEqual(len(rows), 2, "Local CSV should contain header + 1 data row after write_history.")
        self.assertEqual(
            rows[1], 
            [str(x) for x in data],  # Because in write_history we do writer.writerow(values)
            "The row in local CSV should match the data that was written."
        )

        # Now ensure that the Sheets API was called through write_history_to_cloud
        mock_sheet.values.return_value.update.assert_called_once()

    @patch("database.authenticate")
    @patch("database.build")
    def test_update_history(self, mock_build, mock_authenticate):
        """
        Test that update_history clears the remote sheet and then updates 
        it with the local CSV data.
        """
        # Build a mock for the credentials
        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds

        # Build a mock for Sheets
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        # Write an extra line to our local CSV to simulate existing data
        with open(self.history_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["(1,2)", "(3,4)", "robot1", "ai1", "120", "60", "1"])

        # Call the update_history function
        database.update_history()

        # We expect to clear the remote data first
        mock_sheet.values.return_value.clear.assert_called_once()
        # Then we expect to update with local CSV
        mock_sheet.values.return_value.update.assert_called_once()


if __name__ == "__main__":
    unittest.main()
