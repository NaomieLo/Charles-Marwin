# Import your production code
import sys
import os

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))

# Now, import database.py
import database

import unittest
from unittest.mock import patch, MagicMock

class TestDatabaseFunctions(unittest.TestCase):
    @patch("database.build")
    def test_read_history_no_data(self, mock_build):
        """Test read_history when no data is found in Google Sheets"""
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = {"values": []}
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, [])

    @patch("database.build")
    def test_read_history_with_data(self, mock_build):
        """Test read_history when data is present"""
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_sheet.values.return_value.get.return_value.execute.return_value = {
            "values": [["Start", "End", "Robot", "AI", "Distance", "Time", "Cost"]]
        }
        mock_build.return_value = mock_service

        result = database.read_history()
        self.assertEqual(result, [["Start", "End", "Robot", "AI", "Distance", "Time", "Cost"]])

    @patch("database.build")
    def test_write_history_to_cloud(self, mock_build):
        """Test writing to Google Sheets without errors"""
        mock_service = MagicMock()
        mock_sheet = MagicMock()
        mock_service.spreadsheets.return_value = mock_sheet
        mock_build.return_value = mock_service

        database.write_history_to_cloud("dummy_sheet_id", "data/history.csv")
        self.assertTrue(mock_sheet.values.return_value.update.called)

    @patch("database.authenticate")
    @patch("database.build")
    def test_update_history(self, mock_build, mock_authenticate):
        """Test updating Google Sheets from local history.csv"""
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
