import os
import csv
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from datetime import time

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]

sheet_id = "1gtx4iycix_Bxztaj4M0ZfH3afQPs4iIfdQdwKNNYTyc"

TOKEN_PATH = "data/token.json"

def authenticate():
    """Helper function to authenticate users"""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("data/credentials.json", SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)

            #creds = flow.run_local_server(port=0) 
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds

def read_history():
    """Reads data from the history cloud sheet"""
    creds = authenticate()
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        range_name = "history!A1:Z1000"
        result = sheet.values().get(spreadsheetId="1gtx4iycix_Bxztaj4M0ZfH3afQPs4iIfdQdwKNNYTyc", range=range_name).execute()
        values = result.get('values', [])

        if not values:
            print(f'No data found in history.')
            return []

        return values

    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def input_data(startLocation, endLocation, robot, ai, distance, time, cost):
    """A method to validate the data that is being inputted into the database"""
    if not (isinstance(startLocation, tuple) and len(startLocation) == 2 and 
        isinstance(startLocation[0], int) and 1 <= startLocation[0] <= 23041 and
        isinstance(startLocation[1], int) and 1 <= startLocation[1] <= 46081):
        raise ValueError("startLocation must be of format (int, int) within the valid range")

    if not (isinstance(endLocation, tuple) and len(endLocation) == 2 and 
        isinstance(endLocation[0], int) and 1 <= endLocation[0] <= 23041 and
        isinstance(endLocation[1], int) and 1 <= endLocation[1] <= 46081):
            raise ValueError("endLocation must be of format (int, int) within the valid range")
    
    if not isinstance(robot, str) or robot not in ["robot1", "robot2", "robot3"]:
        raise ValueError("robot must be a valid string")
    
    if not isinstance(ai, str) or ai not in ["ai1", "ai2", "ai3"]:
        raise ValueError("ai must be a valid string")

    if not isinstance(distance, (int, float)):
        raise ValueError("distance must be a number")
    #if not isinstance(time, int): #THIS MIGHT BE AN ISSUE SINCE NOT DATETIME
       # raise ValueError("time must be a number")
    if not isinstance(cost, int):
        raise ValueError("cost must be a number")

    data = [startLocation, endLocation, robot, ai, distance, time, cost]
    return data

def write_history_to_cloud(sheet_id, input_csv):
    """Helper method to read data from the local csv file and pushes it to the cloud csv """
    creds = authenticate()
    try:
        #Read data from file
        with open(input_csv, mode='r') as file:
            reader = csv.reader(file)
            csv_data = list(reader)

        if not csv_data:
            print(f"No data found in {input_csv}")
            return

        #create the Google Sheets API client
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        #specify the range 
        range_name = "history!A1"
        body = {
            'values': csv_data
        }

        #update the range in the sheet
        result = sheet.values().update(
            spreadsheetId=sheet_id, range=range_name,
            valueInputOption="RAW", body=body).execute()

        print("Data updated in history.")

    except HttpError as error:
        print(f'An error occurred: {error}')

def write_history(data):
    """ method to write data to the cloud history file """
    try:
        with open("data/history.csv", mode='a', newline='') as file:
            values = data
            writer = csv.writer(file)
            writer.writerow(values)
            file.flush()
        print(f"\nSuccessfully logged.\n")
    except Exception as file_error:
        print(f"Failed to write to file: {file_error}")
    
    #Push to db
    write_history_to_cloud(sheet_id, "data/history.csv")

def update_history():
    """ Helper method to sync local history file with cloud history file """
    creds = authenticate()
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()

        with open("data/history.csv", mode='r') as file:
            reader = csv.reader(file)
            csv_data = list(reader)

        #clear existing data on the Google Sheet
        sheet.values().clear(spreadsheetId="1gtx4iycix_Bxztaj4M0ZfH3afQPs4iIfdQdwKNNYTyc", range="history!A1:Z1000").execute()

        #update the sheet with local CSV data
        result = sheet.values().update(
            spreadsheetId=sheet_id, range="history!A1",
            valueInputOption="RAW", body={'values': csv_data}).execute()

    except HttpError as error:
        print(f'An error occurred: {error}')


#data = input_data((32,232), (4323,232), "robot1", "ai1", 120, 60, 1)
#write_history(data)

#print(read_history())
#update_history()
# authenticate()

if __name__ == "__main__":
    print("Fetching Google Sheets data...")
    # authenticate()
    # history_data = read_history()

    print(history_data)






