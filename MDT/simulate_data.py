# immersive id="adt-data-emulator" type="code" title="Market Digital Twin Data Emulator"
# This script reads mock data and sends updates to an Azure Digital Twins instance.

import json
import time
import os
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential

# --- Configuration ---
ADT_INSTANCE_URL = "https://adt-mdtw-sheila.api.sea.digitaltwins.azure.net" 

MARKET_TWIN_ID = "marketTwin001"

MOCK_DATA_FILE = "mdt_mock_data.json"

# Delay between sending each data point (in seconds)
# Adjust this to simulate real-time updates (e.g., 1 second for fast demo, 3600 for hourly)
UPDATE_INTERVAL_SECONDS = 5

# --- Azure Authentication ---
try:
    # DefaultAzureCredential will try to authenticate using various methods:
    # Environment variables, Managed Identity, Visual Studio Code, Azure CLI, etc.
    # For local development, ensure you are logged into Azure CLI (`az login`)
    # or VS Code with the correct account.
    credential = DefaultAzureCredential()
    dt_client = DigitalTwinsClient(ADT_INSTANCE_URL, credential)
    print(f"Successfully connected to Azure Digital Twins instance: {ADT_INSTANCE_URL}")
except Exception as e:
    print(f"Error connecting to Azure Digital Twins: {e}")
    print("Please ensure you are logged into Azure CLI (`az login`) or VS Code with the correct account,")
    print("and that your ADT_INSTANCE_URL is correct and accessible.")
    exit()

# --- Load Mock Data ---
try:
    with open(MOCK_DATA_FILE, 'r') as f:
        mock_data = json.load(f)
    print(f"Successfully loaded mock data from {MOCK_DATA_FILE}. Total entries: {len(mock_data)}")
except FileNotFoundError:
    print(f"Error: Mock data file '{MOCK_DATA_FILE}' not found.")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from '{MOCK_DATA_FILE}'. Please check file format.")
    exit()

# --- Main Simulation Loop ---
print(f"Starting data simulation for twin '{MARKET_TWIN_ID}'...")
print(f"Updating every {UPDATE_INTERVAL_SECONDS} seconds.")

# Ensure the twin exists before attempting to update it
try:
    dt_client.get_digital_twin(MARKET_TWIN_ID)
    print(f"Twin '{MARKET_TWIN_ID}' found. Proceeding with updates.")
except Exception as e:
    print(f"Error: Twin '{MARKET_TWIN_ID}' not found or inaccessible. Please create it in ADT Explorer first.")
    print(f"Error details: {e}")
    exit()

for i, data_point in enumerate(mock_data):
    # Construct the patch document for updating twin properties
    # The properties in the patch must match the DTDL model properties
    # 'marketPrice', 'demandLevel', 'policyFlag'
    patch = [
        {
            "op": "replace",
            "path": "/marketPrice",
            "value": data_point["price_sgd_per_kwh"]
        },
        {
            "op": "replace",
            "path": "/demandLevel",
            "value": data_point["demand_mw"]
        },
        {
            "op": "replace",
            "path": "/policyFlag",
            "value": data_point["policy_flag"]
        }
    ]

    try:
        # Send the update to the digital twin
        dt_client.update_digital_twin(MARKET_TWIN_ID, patch)
        print(f"[{i+1}/{len(mock_data)}] Updated twin '{MARKET_TWIN_ID}':")
        print(f"  marketPrice: {data_point['price_sgd_per_kwh']}")
        print(f"  demandLevel: {data_point['demand_mw']}")
        print(f"  policyFlag: {data_point['policy_flag']}")
    except Exception as e:
        print(f"Error updating twin '{MARKET_TWIN_ID}' with data point {i+1}: {e}")

    # Wait for the next update interval
    time.sleep(UPDATE_INTERVAL_SECONDS)

print("Data simulation complete.")
