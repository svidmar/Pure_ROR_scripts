
import requests
import urllib.parse
import csv
import os
import time

# Function to handle rate limiting
def rate_limiter(count, start_time):
    max_requests = 2000
    time_frame = 300  # 5 minutes in seconds
    if count >= max_requests:
        elapsed_time = time.time() - start_time
        if elapsed_time < time_frame:
            time.sleep(time_frame - elapsed_time)
        return time.time()  # Reset the start time
    return start_time

# Function to safely get JSON from a response
def get_json_response(response):
    try:
        return response.json()
    except ValueError:
        print(f"Warning: Failed to decode JSON from response. Status code: {response.status_code}")
        return None

# Prompt the user for the API key and set it as an environment variable
api_key = input("Please enter your Pure API key: ")
os.environ['PURE_API_KEY'] = api_key

# Prompt the user for the base URL of the Pure API
pure_api_base_url = input("Please enter the base URL of the Pure API (e.g., https://mypureinstance.com/ws/api): ")

# Initialize variables for pagination and rate limiting
size = 100  # Number of items to fetch per page
offset = 0  # Starting point
total_items = None  # Total number of items to be updated during the first request
request_count = 0
start_time = time.time()

output_file = 'output.csv'

# Write headers only if the file doesn't exist
if not os.path.exists(output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Pure API name", "Pure UUID", "Workflow Step", "Score", "ROR ID", "ROR Name", "Substring", "Chosen", "Matching Type"])

# Process API items and write incrementally
while total_items is None or offset < total_items:
    pure_api_url = f"{pure_api_base_url}/external-organizations?size={size}&offset={offset}"
    headers = {"accept": "application/json", "api-key": os.getenv('PURE_API_KEY')}

    response = requests.get(pure_api_url, headers=headers)
    data = get_json_response(response)

    if not data:
        print(f"Skipping items due to API error. Offset: {offset}")
        offset += size
        continue

    if total_items is None:  # First request, initialize total_items
        total_items = data['count']

    with open(output_file, 'a', newline='') as file:  # Append mode
        writer = csv.writer(file)
        for index, item in enumerate(data['items'], start=1):
            pure_name = item['name']['en_GB']
            pure_uuid = item['uuid']
            workflow_step = item['workflow']['step']
            encoded_name = urllib.parse.quote(pure_name)
            ror_api_url = f"https://api.ror.org/organizations?affiliation={encoded_name}"

            # Rate limiting check
            start_time = rate_limiter(request_count, start_time)
            request_count += 1

            ror_response = requests.get(ror_api_url)
            ror_data = get_json_response(ror_response)

            if ror_data and ror_data['items']:
                best_match = ror_data['items'][0]
                score = best_match.get('score', "No Match")
                ror_id = best_match['organization'].get('id', "No Match")
                ror_name = best_match['organization'].get('name', "No Match")
                substring = best_match.get('substring', "No Match")
                chosen = best_match.get('chosen', "No Match")
                matching_type = best_match.get('matching_type', "No Match")
            else:
                score, ror_id, ror_name, substring, chosen, matching_type = ["No Match"] * 6

            # Write data immediately
            writer.writerow([pure_name, pure_uuid, workflow_step, score, ror_id, ror_name, substring, chosen, matching_type])
            print(f"Processed item {offset + index}/{total_items}: {pure_name}")

    offset += size

print("CSV file is being updated as items are processed.")
