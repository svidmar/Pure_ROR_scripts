
# Pure2ROR2Pure: Pure & ROR Integration Scripts

## Overview
This repository contains a collection of Python scripts designed to facilitate the integration of Research Organization Registry (ROR) IDs with a Pure instance. These scripts are useful for extracting data from a Pure instance, querying the ROR API for matching organizations, and updating the external organizations in Pure instance with ROR IDs.

## Scripts

- **getror-rorapi.py**: Queries the ROR API with external organization names from a Pure instance to find matching ROR IDs.
- **getror-docker.py**: Similar to `getror-rorapi.py` but designed to work with a local ROR API instance, run via Docker. [Info here](https://github.com/ror-community/ror-api) 
- **csv-to-ror_docker.py**: Reads a CSV file containing organization names and UUIDs, queries a local ROR API instance for matches, and generates an output CSV with ROR IDs.
- **writeror2pure.py**: Takes the output CSV from the ROR querying scripts and updates the Pure instance with ROR IDs.

## Requirements

- Python 3.x
- Requests library
- CSV and OS standard libraries (included with Python)
- API key for Pure with read/write rights to the /external-organizations/* endpoint
- Docker (if relevant)

## Setup

1. Clone this repository to your local machine.
2. Ensure you have Python 3.x installed.
3. Install the required Python packages by running `pip install requests`.

## Usage

When running the scripts, you need to input variables such as API keys, base URLs and csv file locations. 

### Querying ROR API

To query the ROR API for organization matches, run:

```bash
python getror-rorapi.py
```

Or, if you're using a local ROR API Docker instance:

```bash
python getror-docker.py
```

### Generating and Updating ROR IDs

To generate a CSV with organization names, UUIDs, and their corresponding ROR IDs:

```bash
python csv-to-ror_docker.py
```

To update your Pure instance with ROR IDs from a generated CSV file:

```bash
python writeror2pure.py
```

## Contributing

Contributions to this repository are welcome. Please fork the repository and submit a pull request with your changes.
