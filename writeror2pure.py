import requests
import json
import csv
import logging

# Setup logging
logging.basicConfig(filename='pure_updates.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Prompt for API key and API base URL
API_KEY = input("Enter your Pure API key: ")
BASE_URL_INPUT = input("Enter the Pure API base (e.g., my.pureinstance.com): ")
API_URL_BASE = f"https://{BASE_URL_INPUT}/ws/api/external-organizations/"

# Function to construct headers for the request
def get_headers():
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

# Fetch external organization data using UUID
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
        logging.error(f"Error fetching data for UUID {uuid}: {e}")
        return None

# Update organization's identifiers with version control
def update_organization(uuid, identifiers, ror_id, version):
    try:
        # Check if ROR ID already exists
        ror_exists = any(
            identifier.get('id') == ror_id and \
            identifier.get('type', {}).get('term', {}).get('en_GB') == "ROR ID"
            for identifier in identifiers
        )

        if ror_exists:
            print(f"ROR ID already exists for UUID: {uuid}. Skipping update.")
            logging.info(f"ROR ID already exists for UUID: {uuid}. Skipping update.")
            return

        url = f"{API_URL_BASE}{uuid}"
        headers = get_headers()
        payload = {
            "version": version,  # Include version for optimistic locking
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
            logging.info(f"Successfully updated UUID: {uuid} with payload: {json.dumps(payload)}")
        else:
            print(f"Error updating data for UUID: {uuid}, Response Code: {response.status_code}")
            logging.error(f"Error updating UUID: {uuid}, Response Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred while updating data for UUID {uuid}: {e}")
        logging.error(f"Error updating data for UUID {uuid}: {e}")

# Main script execution
try:
    with open('output.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            print("Row from CSV:", row)  # Confirm each row is being read
            uuid = row['Pure UUID']
            ror_id = row['ROR ID']
            current_data = fetch_organization(uuid)
            if current_data:
                version = current_data.get('version')  # Extract the version
                identifiers = current_data.get('identifiers', [])
                if version:
                    update_organization(uuid, identifiers, ror_id, version)
                else:
                    print(f"Version not found for UUID: {uuid}. Skipping update to prevent conflicts.")
                    logging.warning(f"Version not found for UUID: {uuid}. Update skipped.")
except FileNotFoundError:
    print("Error: The specified 'output.csv' file was not found.")
    logging.error("The specified 'output.csv' file was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    logging.critical(f"An unexpected error occurred: {e}")
