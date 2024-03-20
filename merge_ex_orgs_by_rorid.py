# Script which can be used to merge external organizations in Pure based on a CSV file containing Pure UUID, Workflow step and ROR ID. 
# Expects columns to be named "Pure UUID", "Workflow Step" and "ROR ID" and delimiter to be ';'
# Sorting logic: External organizations with matching ROR ID's are grouped together, and the the external org with workflow status Approved is set as the merge target.  
# If a group has more than one "approved" external organization per ROR ID, it logs a warning and skips processing for that ROR ID. The rest of the processing proceeds as before, except it now also checks if the ROR ID was skipped due to multiple approvals before attempting to send a merge request.
# If a group has no approved external organisation it logs a warning and skips processing for that ROR ID.
# Log file dumped in script directory

import pandas as pd
import requests
import logging

# Setup logging
logging.basicConfig(filename='merge_requests.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Load the CSV file
file_path = './output_test.csv'  # Update this to the path of your CSV file
df = pd.read_csv(file_path, delimiter=';')

# Sort by 'Approved' workflow status
df['IsApproved'] = df['Workflow Step'] == 'Approved'
df.sort_values(by=['ROR ID', 'IsApproved', 'Pure UUID'], ascending=[True, False, True], inplace=True)

# Check for multiple or no approvals and log if found
def check_multiple_approvals(group):
    approved_count = sum(group['IsApproved'])
    if approved_count > 1:
        logging.warning(f"ROR ID {group.name} has multiple approvals. Skipping.")
        print(f"ROR ID {group.name} has multiple approvals. Skipping.")
        return None
    elif approved_count == 0:
        logging.info(f"ROR ID {group.name} has no approved organizations. Skipping.")
        print(f"ROR ID {group.name} has no approved organizations. Skipping.")
        return None
    else:
        return group['Pure UUID'].tolist()

grouped_uuids = df.groupby('ROR ID').apply(check_multiple_approvals).dropna().to_dict()

# API details
api_url = "https://my-pure-instance.com/ws/api/external-organizations/merge" # Replace with actual Pure API URL
headers = {
    "accept": "application/json",
    "api-key": "pure_apikey",  # Replace with actual Pure API key
    "content-type": "application/json",
}

def send_merge_request(ror_id, uuids):
    payload = {
        "items": [{"uuid": uuid, "systemName": "ExternalOrganization"} for uuid in uuids]
    }
    response = requests.post(api_url, headers=headers, json=payload)
    
    uuids_str = ", ".join(uuids)  # Creating a string of UUIDs for logging
    if response.status_code == 200:
        log_message = f"Successfully sent merge request for ROR ID {ror_id} for UUIDs: {uuids_str}."
    else:
        log_message = f"Failed to send merge request for ROR ID {ror_id} with status code: {response.status_code}, Response: {response.text} For UUIDs: {uuids_str}."

    logging.info(log_message)
    print(log_message)

# Process each ROR ID and its associated UUIDs
for ror_id, uuids in grouped_uuids.items():
    if uuids is not None:  # Checking if the ROR ID was skipped due to multiple approvals
        send_merge_request(ror_id, uuids)
        print("-------------------------------------------------")
