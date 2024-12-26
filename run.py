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

###########################################################

# Access the worksheets
user_input_sheet = SHEET.worksheet("User_Input")
airports_sheet = SHEET.worksheet("Airports")
results_sheet = SHEET.worksheet("Results")


# Function to get the latitude and longitude of an airport from the Airports worksheet
# Latitude in column 2 and Longitude in column 3

def get_lat_lon(airport_code):
    try:
        # Find the row in Airports sheet with the matching airport code
        cell = airports_sheet.find(airport_code)
        row = cell.row
        lat = airports_sheet.cell(row, 2).value
        lon = airports_sheet.cell(row, 3).value
        return lat, lon

    except gspread.exceptions.CellNotFound:
        print(f"There is no coordinates data for Airport {airport_code} .")
        return None, None


# Get the last row of data from User_Input sheet
user_input_data = user_input_sheet.get_all_records()
if user_input_data:
    last_row = user_input_data[-1]  # Get the last row of input data
    origin_airport = last_row.get('Origin_Airport')
    destination_airport = last_row.get('Destination_Airport')

    # Get latitude and longitude for the origin airport
    orig_lat, orig_lon = get_lat_lon(origin_airport)

    # Get latitude and longitude for the destination airport
    dest_lat, dest_lon = get_lat_lon(destination_airport)

    if orig_lat and orig_lon and dest_lat and dest_lon:
        # Prepare the result data
        result_data = [
            origin_airport, orig_lat, orig_lon,
            destination_airport, dest_lat, dest_lon
        ]

        # Find the first empty row in the Results worksheet
        # This assumes that there is no data in the first column of empty rows
        next_empty_row = len(results_sheet.col_values(1)) + 1

        # Store the result data in the next empty row
        results_sheet.insert_row(result_data, next_empty_row)
        print("Results stored in the 'Results' worksheet.")
    else:
        print("Unable to retrieve latitudes and longitudes for the two airports.")
else:
    print("No data found in 'User_Input' worksheet.")

