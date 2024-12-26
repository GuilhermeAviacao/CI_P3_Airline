# Your code goes here.
# You can delete these comments, but do not change the name of this file
# Write your code to expect a terminal of 80 characters wide and 24 rows high

#Libraries
import gspread
from google.oauth2.service_account import Credentials
from gspread import Worksheet

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

#display_airports(SHEET)

#Recording user input in the User_Input worksheet

def record_user_input(sheet, origin, destination):
    """
    Records the origin and destination inputs, provided they are 3 letter airport codes
    """
    # Validate that inputs have 3 characters
    if len(origin) != 3:
        print(f"Invalid origin code: {origin}. An airport code needs to have 3 characters.")
        return

    if len(destination) != 3:
        print(f"Invalid destination code: {destination}. An airport code needs to have 3 characters.")
        return

    try:
        # Open the "User_Input" worksheet
        worksheet = sheet.worksheet("User_Input")

        # Append the user inputs to the next available row
        worksheet.append_row([origin, destination])

        print(f"Inputs recorded: Origin = {origin}, Destination = {destination}")

    except Exception as e:

        print(f"Check Google sheets, error while recording user inputs {e}")

origin = input("Enter the origin airport 3-letter IATA code: ").strip().upper()
destination = input("Enter the destination airport 3-letter IATA code: ").strip().upper()

record_user_input(SHEET, origin, destination)