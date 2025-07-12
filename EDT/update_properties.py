import json
import time
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import AzureCliCredential
from azure.core.exceptions import HttpResponseError

# ------------------------------------------------------------
adt_instance_url = "https://environment-dtw.api.sea.digitaltwins.azure.net"
digital_twin_id = "env_dtw_sit"
mock_data_file = "edt_mock_data.json"
send_delay = 20  # seconds between updates
# ------------------------------------------------------------

# Authenticate with Azure AD
credential = AzureCliCredential()
client = DigitalTwinsClient(adt_instance_url, credential)

# Load your mock data
with open(mock_data_file, "r") as f:
    data_records = json.load(f)

# Loop through records and update the twin's properties
for record in data_records:
    patch = [
        {"op": "replace", "path": "/temperature_C", "value": record.get("temperature_C")},
        {"op": "replace", "path": "/humidity_percent", "value": record.get("humidity_percent")},
        {"op": "replace", "path": "/solar_irradiance_Wm2", "value": record.get("solar_irradiance_Wm2")},
        {"op": "replace", "path": "/cloud_cover_percent", "value": record.get("cloud_cover_percent")}
    ]
    try:
        print(f"Updating twin with data: {record}")
        client.update_digital_twin(digital_twin_id, patch)
        print("✅ Twin updated successfully.")
    except HttpResponseError as e:
        print(f"Error updating twin: {e}")

    time.sleep(send_delay)

print("✅ Simulation complete.")
