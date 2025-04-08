import os
import csv
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock, mock_open
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database


database.TOKEN_PATH = None
database.HISTORY_CSV = None


class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        """
        Creates a temporary directory for token and history file testing.
        The token file is created in a temp directory, and we also create a
        temporary CSV file to simulate local history data.
        """
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        
        with open(self.token_path, "w") as f:
            f.write('{"dummy": "token"}')

        database.TOKEN_PATH = self.token_path

        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        with open(self.history_csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["startLocation", "endLocation", "robot", "ai", "distance", "time", "cost"])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 122])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1220])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1220])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1])
            writer.writerow(["(32, 232)", "(4323, 232)", "robot1", "ai1", 120, 60, 1])

    def tearDown(self):
        """Removes the temporary directory after each test."""
        shutil.rmtree(self.test_dir)

    @patch("database.build")
    @patch("database.authenticate")
    def test_update_history(self, mock_authenticate, mock_build):
        """
        Test that update_history() clears the remote sheet and then updates it
        with the local CSV data.
        """

        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        with open(self.history_csv_path, "r") as file:
            file_data = file.read()

        mock_file = mock_open(read_data=file_data)

        with patch("builtins.open", mock_file):
            database.update_history()

        mock_sheet.values.return_value.clear.assert_called_once()

        mock_sheet.values.return_value.update.assert_called_once()

        update_args = mock_sheet.values.return_value.update.call_args[1]  
        updated_values = update_args["body"]["values"] 

        with open(self.history_csv_path, "r") as file:
            expected_data = list(csv.reader(file))

        self.assertEqual(updated_values, expected_data, "The data uploaded to the cloud should match local history.csv")


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
        Test that input_data() raises ValueError for an invalid startLocation.
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
        Test that write_history() writes data to the local CSV file and calls write_history_to_cloud().
        Since write_history() uses the hard-coded path "data/history.csv", we patch open()
        in the database module to intercept file writes
        """
        data = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        database.write_history(data)

        # Verify that open() was called with "data/history.csv" in append mode.
        mock_file.assert_called_with("data/history.csv", mode="a", newline="")
        # Verify that write_history_to_cloud() was called with the expected arguments.
        mock_write_history_to_cloud.assert_called_once_with(database.sheet_id, "data/history.csv")


    @patch("database.authenticate")
    @patch("database.build")
    def test_update_history(self, mock_build, mock_authenticate):
        """
        Test that update_history() clears the remote sheet and then updates it
        with the local CSV data
        """
        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        with open(self.history_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["(1,2)", "(3,4)", "robot1", "ai1", "120", "60", "1"])

        import builtins
        original_open = builtins.open
        def custom_open(file, mode='r', *args, **kwargs):
            if file == "data/history.csv":
                return original_open(self.history_csv_path, mode, *args, **kwargs)
            return original_open(file, mode, *args, **kwargs)

        with patch("builtins.open", side_effect=custom_open):
            database.update_history()

        mock_sheet.values.return_value.clear.assert_called_once()
        mock_sheet.values.return_value.update.assert_called_once()


if __name__ == "__main__":
    unittest.main()
