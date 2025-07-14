import time
import json
from azure.identity import DefaultAzureCredential
from azure.digitaltwins.core import DigitalTwinsClient

# CONFIGURATION
adt_instance_url = "https://Hibatul-Value-Twin.api.sea.digitaltwins.azure.net" 
twin_id = "VDT"
mock_data_file = "vdt_mock_data.json"
GRID_EMISSION_FACTOR = 0.412
SIMULATION_SPEED_IN_SECONDS = 5 

def main():
    print("--- Starting Comprehensive VDT Simulation (ROI & ESG) ---")
    
    try:
        credential = DefaultAzureCredential()
        client = DigitalTwinsClient(adt_instance_url, credential)
        print(" Successfully authenticated.")

        twin_data = client.get_digital_twin(twin_id)
        initial_investment = twin_data.get('initialInvestment', 1)
        print(f"Fetched Initial Investment from twin '{twin_id}': ${initial_investment}")

    except Exception as e:
        print(f" Failed to connect or get twin data: {e}")
        return

    with open(mock_data_file, 'r') as f:
        mock_data = json.load(f)

    # Initialize cumulative trackers (Operational Cost removed)
    cumulative_revenue = 0.0
    cumulative_carbon_saved = 0.0

    print(f"\n--- Simulating {len(mock_data)} days ---")
    for record in mock_data:
        day = record['day']
        
        #Read source data for the day 
        daily_energy_output = record['dailyEnergyOutput_kWh']
        avg_market_price = record['averageMarketPrice_SGD']
        avg_solar_irradiance = record['averageSolarIrradiance_from_EDT']
        
        #Perform all calculations 
        daily_revenue = round(daily_energy_output * avg_market_price, 2)
        cumulative_revenue += daily_revenue
        
        daily_carbon_saved = round(daily_energy_output * GRID_EMISSION_FACTOR, 2)
        cumulative_carbon_saved += daily_carbon_saved

        
        environmental_score = min(daily_carbon_saved / 750, 1) * 100
        esg_score = round((environmental_score * 0.6) + (75 * 0.2) + (90 * 0.2), 2)

        # Net Profit is now the same as Cumulative Revenue in this simplified model
        net_profit = cumulative_revenue
        roi = round((net_profit / initial_investment) * 100, 4) if initial_investment > 0 else 0
        
        print(f"Day {day}: Daily Revenue: ${daily_revenue}, ESG: {esg_score}, ROI: {roi}%")


        # TWIN UPDATE 
        patch = [
            # Update source properties for the daily snapshot
            {"op": "add", "path": "/source_energyOutput", "value": daily_energy_output},
            {"op": "add", "path": "/source_marketPrice", "value": avg_market_price},
            {"op": "add", "path": "/source_solarIrradiance", "value": avg_solar_irradiance},
            
            # Use the NEW, correct property name for daily revenue
            {"op": "add", "path": "/last_calculated_daily_revenue", "value": daily_revenue},
            
            # Update daily calculated properties
            {"op": "add", "path": "/calculated_carbon_saved", "value": daily_carbon_saved},
            
            # Update cumulative and final score properties
            {"op": "add", "path": "/cumulativeRevenue", "value": round(cumulative_revenue, 2)},
            {"op": "add", "path": "/cumulativeCarbonSaved", "value": round(cumulative_carbon_saved, 2)},
            {"op": "add", "path": "/returnOnInvestment", "value": roi},
            {"op": "add", "path": "/esgScore", "value": esg_score}
        ]

        try:
            client.update_digital_twin(twin_id, patch)
        except Exception as e:
            print(f"   Failed to update twin on day {day}: {e}")
        
        time.sleep(SIMULATION_SPEED_IN_SECONDS)

    print("\n--- Comprehensive Simulation Complete ---")

if __name__ == '__main__':
    main()