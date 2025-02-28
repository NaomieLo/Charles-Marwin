import os
import csv
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock, mock_open
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Adjust the import path to where your database.py is located.
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
import database

database.TOKEN_PATH = None

database.HISTORY_CSV = None

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        """
        Creates a temporary directory for token and history file testing.
        """
        logger.debug("Setting up temporary test environment.")
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
        logger.debug("Test CSV file created with sample data.")

    def tearDown(self):
        """Removes the temporary directory after each test."""
        logger.debug("Cleaning up temporary test environment.")
        shutil.rmtree(self.test_dir)

    @patch("database.build")
    @patch("database.authenticate")
    def test_update_history(self, mock_authenticate, mock_build):
        """Test that update_history() clears the remote sheet and then updates it."""
        logger.debug("Running test_update_history.")
        mock_creds = MagicMock()
        mock_authenticate.return_value = mock_creds
        
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service
        
        with open(self.history_csv_path, "r") as file:
            file_data = file.read()
        
        with patch("builtins.open", mock_open(read_data=file_data)):
            database.update_history()
        
        mock_sheet.values.return_value.clear.assert_called_once()
        mock_sheet.values.return_value.update.assert_called_once()
        logger.debug("Google Sheets API called successfully for updating history.")

    def test_input_data_valid(self):
        """Test that input_data() returns the correct list of values for valid inputs."""
        logger.debug("Running test_input_data_valid.")
        start = (32, 232)
        end = (4323, 232)
        robot = "robot1"
        ai = "ai1"
        distance = 120
        travel_time = 60
        cost = 1
        
        result = database.input_data(start, end, robot, ai, distance, travel_time, cost)
        expected = [start, end, robot, ai, distance, travel_time, cost]
        logger.debug(f"Expected: {expected}, Got: {result}")
        self.assertEqual(result, expected)

    def test_input_data_invalid(self):
        """Test that input_data() raises ValueError for an invalid startLocation."""
        logger.debug("Running test_input_data_invalid.")
        start = ("invalid", 232)
        end = (4323, 232)
        robot = "robot1"
        ai = "ai1"
        distance = 120
        travel_time = 60
        cost = 1
        
        with self.assertRaises(ValueError):
            database.input_data(start, end, robot, ai, distance, travel_time, cost)
        logger.debug("ValueError correctly raised for invalid input data.")

    @patch("database.build")
    def test_read_history_with_data(self, mock_build):
        """Test read_history() returns a list of lists when the Sheets API provides data."""
        logger.debug("Running test_read_history_with_data.")
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        fake_data = [["start", "end", "robot", "ai", "distance", "time", "cost"],
                     ["(1,2)", "(3,4)", "robot1", "ai1", "100", "50", "10"]]
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": fake_data}
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        result = database.read_history()
        logger.debug(f"Retrieved history data: {result}")
        self.assertEqual(result, fake_data)

    @patch("database.write_history_to_cloud")
    @patch("database.open", new_callable=mock_open, read_data="start,end,robot,ai,distance,time,cost\n")
    def test_write_history(self, mock_file, mock_write_history_to_cloud):
        """Test that write_history() writes data to the local CSV file and calls write_history_to_cloud."""
        logger.debug("Running test_write_history.")
        data = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        database.write_history(data)

        mock_file.assert_called_with("data/history.csv", mode="a", newline="")
        mock_write_history_to_cloud.assert_called_once_with(database.sheet_id, "data/history.csv")
        logger.debug("write_history() successfully wrote to CSV and called write_history_to_cloud().")

if __name__ == "__main__":
    unittest.main()
