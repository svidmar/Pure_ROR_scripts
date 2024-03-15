import requests
import urllib.parse
import csv
import os

# Function to safely get JSON from a response
def get_json_response(response):
    try:
        return response.json()
    except ValueError:
        print(f"Warning: Failed to decode JSON from response. Status code: {response.status_code}")
        return None

# Prompt the user for the CSV file path
csv_file_path = input("Please enter the path to your CSV file: ")

# Initialize variables
extracted_data = []

# Read data from the CSV file
with open(csv_file_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        pure_name = row['Name']
        pure_uuid = row['UUID']
        workflow_step = row['Current workflow step']
        encoded_name = urllib.parse.quote(pure_name)
        ror_api_url = f"http://localhost:9292/organizations?affiliation={encoded_name}"

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

        extracted_data.append([pure_name, pure_uuid, workflow_step, score, ror_id, ror_name, substring, chosen, matching_type])
        print(f"Processed item: {pure_name}")

# Generate a CSV file with the extracted data
with open('output.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Pure API name", "Pure UUID", "Workflow Step", "Score", "ROR ID", "ROR Name", "Substring", "Chosen", "Matching Type"])
    writer.writerows(extracted_data)

print("CSV file has been created with the extracted data.")
