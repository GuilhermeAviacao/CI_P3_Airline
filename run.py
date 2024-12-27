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
# Credits for the airport database from https://ourairports.com/data/

user_input_sheet = SHEET.worksheet("User_Input")
airports_sheet = SHEET.worksheet("Airports")
results_sheet = SHEET.worksheet("Results")

# Function to record user input for origin and destination

def get_user_input():
    """
    Asks for the user to enter origin and destination in IATA code format
    """

    # Prompt the user
    print("\nPlease make your inputs using the 3-letter IATA codes.")
    origin = input("\nEnter the origin airport: \n").strip().upper()
    destination = input("Enter the destination airport: \n").strip().upper()

    # Checks if Destination is different from Origin.
    if origin == destination:
        print(f" {origin} cannot be origin and destination. Please input another destination.")
        raise ValueError("Destination must be different from origin.")

    # Checks if input is in the IATA 3-letters standard.
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

    #"Function to get the latitude and longitude of an airport from the Airports database worksheet"

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


def view_all_airports():
    """
    Fetch and display all airport records from the Airports worksheet.
    """
    try:
        all_airport_rows = airports_sheet.get_all_values()
        if all_airport_rows:
            print("\nAvailable Airports:")
            for row in all_airport_rows:
                print(f"IATA Code: {row[0]}, Latitude: {row[1]}, Longitude: {row[2]}, Name: {row[3]}, Municipality: {row[4]}, Country: {row[5]}, Continent: {row[6]} ")
        else:
            print("No records found in the Airports database.")

    except Exception as e:
        print(f"Error accessing Airports sheet: {e}")


#Function to get all results from user route inputs
def view_all_results():
    """
    Fetch and display all user_input records from the Results worksheet.
    """
    try:
        view_all_results = results_sheet.get_all_values()
        if view_all_results:
            print("\nPrior calculated route results from user inputs:")
            for row in view_all_results:
                print(f"Origin Airport : {row[0]}, Orig_Lat: {row[1]}, Orig_Lon: {row[2]}, Destination Airport : {row[3]}, Dest_Lat: {row[4]}, Dest_Lon: {row[5]}, Distance_Km: {row[6]}")
        else:
            print("No records found in the Results Sheet.")

    except Exception as e:
        print(f"Error accessing Results sheet: {e}")

#Calling of main function

def main():
    print("\nWelcome to the Airport Distance Calculator!")

    while True:
        try:

            print("\n1. Calculation of Airport Distances. Enter a new origin and destination.")
            print("2. View all available airports.")
            print("3. View all prior calculations.")
            print("4. Exit.")

            user_choice = input("\nPlease select an option (1/2/3/4): \n").strip()

            #Airport Distance Calculation

            if user_choice == "1":

                get_user_input()
                print("\nPlease wait for calculation...")

                origin_airport, destination_airport, distance_km = printing_distance_km_according_to_input()

                if origin_airport and destination_airport and distance_km is not None:
                    print(f"\nThe distance between {origin_airport} and {destination_airport} is {distance_km} Kms.")
                    print("\nHave a nice trip!")
                else:
                    print("There was an issue with the distance calculation.")

            # Query to Display all airports in the database
            elif user_choice == "2":
                view_all_airports()  # Display all available airports
                print("\nEnd of Airport database results.")

            # Query to Display all results in the database
            elif user_choice == "3":
                view_all_results()  # Display all available airports
                print("\nEnd of calculated results sheet.")

            # Exit for the program
            elif user_choice == "4":
                print("\nThanks for using the Airport Distance Calculator!")
                break

            else:
                print("Invalid option. Please select 1, 2, 3 or 4.")

        except Exception as err:
            print(f"An error occurred: {err}")



# Calls the main function
main()
