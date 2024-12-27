import gspread, math
from google.oauth2.service_account import Credentials

# Constants
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('CIP3_Airline')

# Worksheets
user_input_sheet = SHEET.worksheet("User_Input")
airports_sheet = SHEET.worksheet("Airports")
results_sheet = SHEET.worksheet("Results")

# Function to record user input for origin and destination

def get_user_input():
    """
    Asks for the user to enter origin and destination in IATA code format
    """

    # Prompt the user
    print("Please make your inputs using the 3-letter IATA codes.")
    origin = input("Enter the origin airport: ").strip().upper()
    destination = input("Enter the destination airport: ").strip().upper()

    # CheckS if Destination is different from Origin.
    if origin == destination:
        print(f" {origin} cannot be origin and destination. Please input another destination.")
        raise ValueError("Destination must be different from origin.")

    # Check if input is in the IATA 3-letters standard.
    if len(origin) != 3 or len(destination) != 3:
        print(f"Invalid codes: {origin}, {destination}. Both must be 3-letter IATA codes.")
        raise ValueError("Invalid IATA codes length.")

    # Checks that both codes contain letters only
    if not origin.isalpha() or not destination.isalpha():
        print(f"Invalid codes: {origin}, {destination}. Both must contain letters only.")
        raise ValueError("Invalid IATA codes, must contain letters only.")

    # Gets the data base list of all airport codes .
    try:
        all_airport_rows = airports_sheet.get_all_values()
        valid_codes = {row[0].upper() for row in all_airport_rows if row}
    except Exception as e:
        print(f"Error accessing Airports sheet: {e}")
        raise Exception("Error accessing Airports sheet.")

    # Check for existence of origin and destination
    if origin not in valid_codes:
        print(f"Invalid origin code: {origin} does not exist in the Airports sheet.")
        raise ValueError("Invalid origin code.")

    if destination not in valid_codes:
        print(f"Invalid destination code: {destination} does not exist in the Airports sheet.")
        raise ValueError("Invalid destination code.")

    # Appends the User Input Sheet with valid Origin and Destination records.
    try:
        user_input_sheet.append_row([origin, destination])
        print(f"Inputs recorded: Origin = {origin}, Destination = {destination}")

    except Exception as e:
        print(f"Error while recording inputs: {e}")
        raise Exception("Error while recording inputs.")


# Function to get the latitude and longitude of an airport from the Airports database worksheet
def get_lat_lon(airport_code):
    try:
        cell = airports_sheet.find(airport_code)
        row = cell.row
        lat = float(airports_sheet.cell(row, 2).value)
        lon = float(airports_sheet.cell(row, 3).value)
        return lat, lon

    except gspread.exceptions.CellNotFound:
        print(f"Airport {airport_code} not found in Airports sheet.")
        return None, None


# Function to calculate distance using Great Circle Distance formula
# Reference to Ed Williams Aviation Formulary: https://edwilliams.org/avform147.htm#Dist

def calculate_distance_km(lat1, lon1, lat2, lon2):
    R = 6371.2  # Radius of Earth in Kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c)

# Function to Print the distance in the Results worksheet
def print_distance_results_sheet(row_index, orig_lat, orig_lon, dest_lat, dest_lon):
    try:
        distance_km = calculate_distance_km(orig_lat, orig_lon, dest_lat, dest_lon)

        results_sheet.update_cell(row_index, 7, distance_km)

        return distance_km  # Return the calculated distance
    except ValueError as e:
        print(f"Error calculating distance for row {row_index}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in row {row_index}: {e}")
        return None

# Fetching and displaying the last user input
def printing_distance_km_according_to_input():
    user_input_data = user_input_sheet.get_all_records()
    if user_input_data:
        last_row = user_input_data[-1]
        origin_airport = last_row.get('Origin_Airport')
        destination_airport = last_row.get('Destination_Airport')

        orig_lat, orig_lon = get_lat_lon(origin_airport)
        dest_lat, dest_lon = get_lat_lon(destination_airport)

        if orig_lat and orig_lon and dest_lat and dest_lon:
            result_data = [
                origin_airport, orig_lat, orig_lon,
                destination_airport, dest_lat, dest_lon
            ]

            # Insert the result data into the next available row in the 'Results' worksheet
            next_empty_row = len(results_sheet.col_values(1)) + 1
            results_sheet.insert_row(result_data, next_empty_row)
            #print("Results stored in the 'Results' worksheet.")

            # distance calculation
            distance_km = print_distance_results_sheet(next_empty_row, orig_lat, orig_lon, dest_lat, dest_lon)

            if distance_km is not None:
                # Return the final message with the calculated distance
                return origin_airport, destination_airport, distance_km
            else:
                print("Failed to calculate distance.")

        else:
            print("Unable to retrieve latitudes and longitudes.")

    else:
        print("No data found in 'User_Input' worksheet.")

#Main function calling the program sequence
def main():
    while True:
        try:
            print("This program will calculate the distance in Km between two airports.")
            get_user_input()
            print("Please wait for calculation...")

            origin_airport, destination_airport, distance_km = printing_distance_km_according_to_input()

            if origin_airport and destination_airport and distance_km is not None:
                print(f"The distance between {origin_airport} and {destination_airport} is {distance_km} Km.")
                print("Calculation complete.")
            else:
                print("There was an issue with the distance calculation.")

            # Ask the user if another input is wanted
            user_choice = input("Do you want to input another airport pair? (yes/no): ").strip().lower()
            if user_choice != 'yes':
                print("Thanks for your input! Have a nice trip!")
                break  # Exit the loop if the user doesn't want to continue

        except Exception as err:
            print(f"An error occurred: {err}")
            #print("The program will stop now.")
            #break  # Stop the program if there is any error in get_user_input()

# Calling the main function
main()