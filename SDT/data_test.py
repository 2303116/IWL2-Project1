import json
import time
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# -----------------------------
# CONFIGURATION
# -----------------------------
adt_instance_url = "https://SDT-r.api.sea.digitaltwins.azure.net"  # Replace with your instance URL
twin_id = "SDTw1"  # Replace with your System Twin ID
mock_data_file = "sdt_mock_data.json"  # Your mock dataset JSON file
send_interval_seconds = 5  # Time delay between sending each record

# -----------------------------
# AUTHENTICATE USING AZURE SDK
# -----------------------------
try:
    credential = DefaultAzureCredential()
    client = DigitalTwinsClient(adt_instance_url, credential)
    print("[INFO] Connected to Azure Digital Twins successfully.")
except Exception as e:
    print("[ERROR] Failed to authenticate:", e)
    exit(1)

# -----------------------------
# LOAD MOCK DATA
# -----------------------------
try:
    with open(mock_data_file, "r") as f:
        mock_data = json.load(f)
    print(f"[INFO] Loaded {len(mock_data)} mock records from {mock_data_file}.")
except Exception as e:
    print("[ERROR] Failed to read mock data file:", e)
    exit(1)

# -----------------------------
# SEND MOCK DATA
# -----------------------------
for idx, record in enumerate(mock_data):
    print(f"\n[INFO] Sending data point {idx + 1}/{len(mock_data)}: {record}")

    # Validate required fields
    required_fields = ["powerOutput", "panelTemp", "status"]
    if not all(field in record for field in required_fields):
        print(f"[ERROR] Missing fields in record: {record}")
        continue

    # Prepare PATCH payload
    patch_payload = [
        {"op": "add", "path": "/powerOutput", "value": record["powerOutput"]},
        {"op": "add", "path": "/panelTemp", "value": record["panelTemp"]},
        {"op": "add", "path": "/status", "value": record["status"]}
    ]

    # Send update
    try:
        client.update_digital_twin(twin_id, patch_payload)
        print(f"Updated twin '{twin_id}':")
        print(f"  timestamp: {record['timestamp']}")
        print(f"  powerOutput: {record['powerOutput']}")
        print(f"  panelTemp: {record['panelTemp']}")
        print(f"  status: {record['status']}")
    except HttpResponseError as e:
        print(f"[ERROR] Failed to update twin '{twin_id}': {e.message}")

    time.sleep(send_interval_seconds)

print("\n[INFO] Finished sending all mock data.")
