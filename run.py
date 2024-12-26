# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

#Libraries
import gspread
from google.oauth2.service_account import Credentials

# API Connection
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('CIP3_Airline')

# First function to get data and test the API

def display_airports(sheet):
    """
    Gets data from 'Airports' sheet from Google API and displays them all.
    """
    try:
        # Select the 'Airports' worksheet
        worksheet = sheet.worksheet("Airports")

        # Get all data from the sheet
        data = worksheet.get_all_records()

        # Display the data
        for row in data:
            print(row)

        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

display_airports(SHEET)