# # command to run, python -m unittest discover -s test/data_test -p "test_history.py"

# import os
# import csv
# import tempfile
# import shutil
# import unittest
# from unittest.mock import patch, MagicMock


# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
# import database

# database.TOKEN_PATH = None
# database.HISTORY_CSV = None

# class TestDatabaseFunctions(unittest.TestCase):
#     def setUp(self):
#         # Create a temporary directory to simulate the 'data' folder for file I/O
#         self.test_dir = tempfile.mkdtemp()
#         self.token_path = os.path.join(self.test_dir, "token.json")
#         self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        
#         # Create a dummy token file so that authentication functions don't trigger a real login
#         with open(self.token_path, "w") as token_file:
#             token_file.write('{"dummy": "token"}')
        
#         # Override file paths in the database module for testing purposes
#         database.TOKEN_PATH = self.token_path
#         database.HISTORY_CSV = self.history_csv_path
        
#         # Create an initial dummy history.csv file (with a header row)
#         with open(self.history_csv_path, "w", newline="") as csv_file:
#             writer = csv.writer(csv_file)
#             writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])

#     def tearDown(self):
#         # Clean up temporary directory after tests run
#         shutil.rmtree(self.test_dir)

#     def test_input_data_valid(self):
#         """input_data should return correctly formatted data for valid inputs."""
#         data = database.input_data((32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
#         expected = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
#         self.assertEqual(data, expected)

#     def test_input_data_invalid(self):
#         """input_data should raise ValueError for an invalid startLocation."""
#         with self.assertRaises(ValueError):
#             database.input_data(("invalid", 232), (4323, 232), "robot1", "ai1", 120, 60, 1)

#     @patch("database.build")
#     def test_read_history_no_data(self, mock_build):
#         """Test read_history returns an empty list when the cloud sheet has no data."""
#         # Set up a fake Sheets API response that returns no values
#         fake_response = {"values": []}
#         mock_service = MagicMock()
#         mock_sheet = MagicMock()
#         mock_service.spreadsheets.return_value = mock_sheet
#         mock_sheet.values.return_value.get.return_value.execute.return_value = fake_response
#         mock_build.return_value = mock_service

#         result = database.read_history()
#         self.assertEqual(result, [])

#     @patch("database.build")
#     def test_read_history_with_data(self, mock_build):
#         """Test read_history returns the expected data when present."""
#         fake_data = [["start", "end", "robot", "ai", "distance", "time", "cost"]]
#         mock_service = MagicMock()
#         mock_sheet = MagicMock()
#         mock_service.spreadsheets.return_value = mock_sheet
#         mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": fake_data}
#         mock_build.return_value = mock_service

#         result = database.read_history()
#         self.assertEqual(result, fake_data)

#     @patch("database.build")
#     def test_write_history_to_cloud(self, mock_build):
#         """Test write_history_to_cloud triggers an update on the cloud sheet."""
#         # Append a new row to our temporary history.csv
#         with open(self.history_csv_path, "a", newline="") as file:
#             writer = csv.writer(file)
#             writer.writerow(["(32,232)", "(4323,232)", "robot1", "ai1", 120, 60, 1])

#         mock_service = MagicMock()
#         mock_sheet = MagicMock()
#         mock_service.spreadsheets.return_value = mock_sheet
#         mock_build.return_value = mock_service

#         database.write_history_to_cloud("dummy_sheet_id", self.history_csv_path)
#         self.assertTrue(mock_sheet.values.return_value.update.called)

#     @patch("database.authenticate")
#     @patch("database.build")
#     def test_update_history(self, mock_build, mock_authenticate):
#         """Test update_history clears and then updates the cloud sheet."""
#         # Write dummy data to the local history.csv file
#         with open(self.history_csv_path, "w", newline="") as file:
#             writer = csv.writer(file)
#             writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])

#         mock_creds = MagicMock()
#         mock_authenticate.return_value = mock_creds
#         mock_service = MagicMock()
#         mock_sheet = MagicMock()
#         mock_service.spreadsheets.return_value = mock_sheet
#         mock_build.return_value = mock_service

#         database.update_history()
#         self.assertTrue(mock_sheet.values.return_value.clear.called)
#         self.assertTrue(mock_sheet.values.return_value.update.called)

# if __name__ == "__main__":
#     unittest.main()
import os
import csv
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

# Add the path to the 'data' folder so we can import database.py
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))

import database

database.TOKEN_PATH = None
database.HISTORY_CSV = None

class TestDatabaseFunctions(unittest.TestCase):
    def setUp(self):
        print("Setting up test environment...")
        self.test_dir = tempfile.mkdtemp()
        self.token_path = os.path.join(self.test_dir, "token.json")
        self.history_csv_path = os.path.join(self.test_dir, "history.csv")
        
        with open(self.token_path, "w") as token_file:
            token_file.write('{"dummy": "token"}')
        
        database.TOKEN_PATH = self.token_path
        database.HISTORY_CSV = self.history_csv_path
        
        with open(self.history_csv_path, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["start", "end", "robot", "ai", "distance", "time", "cost"])
        print("Test environment setup complete.")

    def tearDown(self):
        print("Tearing down test environment...")
        shutil.rmtree(self.test_dir)
        print("Test environment cleaned up.")

    def test_input_data_valid(self):
        print("Running test_input_data_valid...")
        data = database.input_data((32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
        expected = [(32, 232), (4323, 232), "robot1", "ai1", 120, 60, 1]
        print("Result:", data)
        self.assertEqual(data, expected)

    def test_input_data_invalid(self):
        print("Running test_input_data_invalid...")
        with self.assertRaises(ValueError):
            database.input_data(("invalid", 232), (4323, 232), "robot1", "ai1", 120, 60, 1)
        print("ValueError was successfully raised.")

    @patch("database.build")
    def test_read_history_no_data(self, mock_build):
        print("Running test_read_history_no_data...")
        fake_response = {"values": []}
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = fake_response
        mock_build.return_value = mock_service

        result = database.read_history()
        print("Result:", result)
        self.assertEqual(result, [])

    @patch("database.build")
    def test_read_history_with_data(self, mock_build):
        print("Running test_read_history_with_data...")
        fake_data = [["start", "end", "robot", "ai", "distance", "time", "cost"]]
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": fake_data}
        mock_build.return_value = mock_service

        result = database.read_history()
        print("Result:", result)
        self.assertEqual(result, fake_data)

    @patch("database.build")
    def test_write_history_to_cloud(self, mock_build):
        print("Running test_write_history_to_cloud...")
        with open(self.history_csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["(32,232)", "(4323,232)", "robot1", "ai1", 120, 60, 1])

        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        database.write_history_to_cloud("dummy_sheet_id", self.history_csv_path)
        print("Cloud write called?", mock_sheet.values.return_value.update.called)
        self.assertTrue(mock_sheet.values.return_value.update.called)

    @patch("database.authenticate")
    @patch("database.build")
    def test_update_history(self, mock_build, mock_authenticate):
        print("Running test_update_history...")
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
        print("Cloud sheet cleared?", mock_sheet.values.return_value.clear.called)
        print("Cloud sheet updated?", mock_sheet.values.return_value.update.called)
        self.assertTrue(mock_sheet.values.return_value.clear.called)
        self.assertTrue(mock_sheet.values.return_value.update.called)

if __name__ == "__main__":
    unittest.main()
