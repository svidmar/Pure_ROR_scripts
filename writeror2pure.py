import requests
import json
import csv

# Prompt for API key and API base URL
API_KEY = input("Enter your API key: ")
API_URL_BASE = input("Enter the API base URL (e.g., https://my.pureinstance.com/ws/api/external-organizations/): ")

# Function to construct headers for the request
def get_headers():
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

# Fetch organization data using UUID
def fetch_organization(uuid):
    try:
        url = f"{API_URL_BASE}{uuid}"
        headers = get_headers()
        print("Fetching organization data for UUID:", uuid)
        response = requests.get(url, headers=headers)
        print(f"Response Code: {response.status_code}, URL: {url}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data for UUID: {uuid}, Response Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching data for UUID {uuid}: {e}")
        return None

# Update organization's identifiers
def update_organization(uuid, identifiers, ror_id):
    try:
        url = f"{API_URL_BASE}{uuid}"
        headers = get_headers()
        payload = {
            "identifiers": identifiers + [{
                "typeDiscriminator": "ClassifiedId",
                "id": ror_id,
                "type": {
                    "uri": "/dk/atira/pure/ueoexternalorganisation/ueoexternalorganisationsources/ror",
                    "term": {
                        "en_GB": "ROR ID",
                        "da_DK": "ROR ID"
                    }
                }
            }]
        }
        print("Updating organization for UUID:", uuid)
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        print(f"Response Code: {response.status_code}, URL: {url}")
        if response.status_code in [200, 204]:
            print(f"Successfully updated UUID: {uuid}")
        else:
            print(f"Error updating data for UUID: {uuid}, Response Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while updating data for UUID {uuid}: {e}")

# Main script execution
try:
    with open('output.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print("Row from CSV:", row)  # Confirm each row is being read
            uuid = row['Pure UUID']
            ror_id = row['ROR ID']
            current_data = fetch_organization(uuid)
            if current_data:
                identifiers = current_data.get('identifiers', [])
                update_organization(uuid, identifiers, ror_id)
except FileNotFoundError:
    print("Error: The specified 'output.csv' file was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
