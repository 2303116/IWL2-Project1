import threading
import time
import json
import os
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient

# Shared ADT Instance URL
ADT_INSTANCE_URL = os.getenv("ADT_INSTANCE_URL", "https://adt-smartfintech-central.api.sea.digitaltwins.azure.net")

# Digital Twin IDs
EDT_ID = "EDT"
MDT_ID = "MDT"
SDT_ID = "SDT"
VDT_ID = "VDT"

# Mock Data Files
EDT_FILE = "edt_mock_data_24.json"
MDT_FILE = "mdt_mock_data.json"
SDT_FILE = "sdt_mock_data.json"
VDT_FILE = "vdt_mock_data_24.json"

# Constants
DELAY = int(os.getenv("SIMULATION_DELAY", 5))
GRID_EMISSION_FACTOR = float(os.getenv("GRID_EMISSION_FACTOR", 0.412))

# Shared client
credential = DefaultAzureCredential()
client = DigitalTwinsClient(ADT_INSTANCE_URL, credential)

def log(msg):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

def get_patch_op(twin_id, prop_path, value):
    try:
        prop_name = prop_path.lstrip('/')
        twin = client.get_digital_twin(twin_id)
        op = "replace" if prop_name in twin else "add"
        return {"op": op, "path": prop_path, "value": value}
    except Exception as e:
        log(f"❌ Error fetching twin {twin_id} for patch: {e}")
        return None

def edt_emulator():
    try:
        with open(EDT_FILE) as f:
            data = json.load(f)
        for record in data:
            patch = list(filter(None, [
                get_patch_op(EDT_ID, "/temperature_C", record["temperature_C"]),
                get_patch_op(EDT_ID, "/humidity_percent", record["humidity_percent"]),
                get_patch_op(EDT_ID, "/solar_irradiance_Wm2", record["solar_irradiance_Wm2"]),
                get_patch_op(EDT_ID, "/cloud_cover_percent", record["cloud_cover_percent"])
            ]))
            if patch:
                client.update_digital_twin(EDT_ID, patch)
                log("🌿 EDT updated.")
            time.sleep(DELAY)
    except Exception as e:
        log(f"❌ EDT emulator error: {e}")

def mdt_emulator():
    try:
        with open(MDT_FILE) as f:
            data = json.load(f)
        for record in data:
            patch = list(filter(None, [
                get_patch_op(MDT_ID, "/marketPrice", record["price_sgd_per_kwh"]),
                get_patch_op(MDT_ID, "/demandLevel", record["demand_mw"]),
                get_patch_op(MDT_ID, "/policyFlag", record["policy_flag"])
            ]))
            if patch:
                client.update_digital_twin(MDT_ID, patch)
                log("📊 MDT updated.")
            time.sleep(DELAY)
    except Exception as e:
        log(f"❌ MDT emulator error: {e}")

def sdt_emulator():
    try:
        with open(SDT_FILE) as f:
            data = json.load(f)
        for record in data:
            patch = list(filter(None, [
                get_patch_op(SDT_ID, "/powerOutput", record["powerOutput"]),
                get_patch_op(SDT_ID, "/panelTemp", record["panelTemp"]),
                get_patch_op(SDT_ID, "/status", record["status"])
            ]))
            if patch:
                client.update_digital_twin(SDT_ID, patch)
                log("⚙️ SDT updated.")
            time.sleep(DELAY)
    except Exception as e:
        log(f"❌ SDT emulator error: {e}")

def vdt_emulator():
    try:
        with open(VDT_FILE) as f:
            data = json.load(f)

        twin_data = client.get_digital_twin(VDT_ID)
        initial_investment = twin_data.get('initialInvestment', 1_000_000)
        cumulative_revenue = 0.0
        cumulative_carbon = 0.0

        log("💰 Starting VDT emulation with cross-twin data flow demonstration...")

        total_hours = len(data)
        ANNUAL_HOURS = 24 * 365

        for idx, record in enumerate(data, start=1):
            energy = record.get("hourlyEnergyOutput_kWh", 0)
            price = record.get("averageMarketPrice_SGD", 0)
            irradiance = record.get("averageSolarIrradiance_from_EDT", 0)

            # Input validation
            if energy < 0 or price < 0 or irradiance < 0:
                log(f"⚠️ Invalid input data at step {idx}, skipping...")
                continue

            log(f"Step {idx}:")
            log(f"  ▶️ Energy Output (SDT source): {energy} kWh")
            log(f"  ▶️ Market Price (MDT source): SGD {price:.2f}/kWh")
            log(f"  ▶️ Solar Irradiance (EDT source): {irradiance} W/m²")

            revenue = round(energy * price, 2)
            cumulative_revenue += revenue
            carbon = round(energy * GRID_EMISSION_FACTOR, 2)
            cumulative_carbon += carbon

            env_score = min(carbon / 750, 1) * 100
            esg = round((env_score * 0.6) + (75 * 0.2) + (90 * 0.2), 2)

            roi_decimal = cumulative_revenue / initial_investment
            roi_percent = round(roi_decimal * 100, 4)

            log(f"  ▶️ Revenue this step: SGD {revenue:.2f}")
            log(f"  ▶️ Cumulative Revenue: SGD {cumulative_revenue:.2f}")
            log(f"  ▶️ Carbon Saved this step: {carbon} kg")
            log(f"  ▶️ Cumulative Carbon Saved: {cumulative_carbon:.2f} kg")
            log(f"  ▶️ ESG Score: {esg}")
            log(f"  ▶️ Return on Investment (ROI): {roi_percent}%")

            patch = list(filter(None, [
                get_patch_op(VDT_ID, "/source_energyOutput", energy),
                get_patch_op(VDT_ID, "/source_marketPrice", price),
                get_patch_op(VDT_ID, "/source_solarIrradiance", irradiance),
                get_patch_op(VDT_ID, "/last_calculated_daily_revenue", revenue),
                get_patch_op(VDT_ID, "/calculated_carbon_saved", carbon),
                get_patch_op(VDT_ID, "/cumulativeRevenue", round(cumulative_revenue, 2)),
                get_patch_op(VDT_ID, "/cumulativeCarbonSaved", round(cumulative_carbon, 2)),
                get_patch_op(VDT_ID, "/returnOnInvestment", roi_percent),
                get_patch_op(VDT_ID, "/esgScore", esg)
            ]))

            if patch:
                client.update_digital_twin(VDT_ID, patch)

            time.sleep(DELAY)

    except Exception as e:
        log(f"❌ VDT emulator error: {e}")

if __name__ == "__main__":
    log("🚀 Starting unified simulation for all Digital Twins...\n")

    # Run EDT, MDT, SDT in parallel, then VDT after (to avoid race conditions)
    threads = [
        threading.Thread(target=edt_emulator),
        threading.Thread(target=mdt_emulator),
        threading.Thread(target=sdt_emulator)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Run VDT emulator last to ensure source data updated
    vdt_emulator()

    log("\n✅ All Digital Twin simulations completed.")
