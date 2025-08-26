import sys
import os
import pandas as pd
import datetime as dt
import time
sys.path.append((os.path.abspath('')))

from const import Config
from fourjaw import FourJaw

# --- Helper Functions from Data Processor ---
def get_shift_info(timestamp: pd.Timestamp) -> tuple:
    """Determines the shift and day of the week for a given timestamp."""
    day_name = timestamp.strftime('%A')
    current_time = timestamp.time()
    if config.DAY_SHIFT_START <= current_time < config.DAY_SHIFT_END:
        shift_name = "DAY"
    else:
        shift_name = "NIGHT"
    return shift_name, day_name.upper()

def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Performs all data wrangling on the final, aggregated DataFrame."""
    if df.empty:
        return df
        
    # Add name of machine from the ID map
    df.insert(0, 'name', df['machine_id'].copy().apply(lambda x: config.MACHINE_ID_MAP.get(x, 'Unknown')))
    
    # Convert timestamps
    df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='ISO8601')
    df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], format='ISO8601')
    
    # Calculate duration
    df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()
    
    # Add shift and day info
    df['shift'], df['day_of_week'] = zip(*df['start_timestamp'].apply(get_shift_info))
    
    # Create utilisation category
    df['utilisation_category'] = df['productivity'].apply(lambda x: x.upper()) + " " + df['classification']
    return df

# --- Main Logic with Rolling Time-Window ---
def main():
    api = FourJaw()
    
    # --- Configuration ---
    days_to_fetch = 3
    
    # --- Loop through each machine ---
    for machine_id in config.MACHINE_IDS:
        machine_name = config.MACHINE_ID_MAP.get(machine_id, machine_id)
        print(f"\n--- Starting data fetch for machine: {machine_name} ---")
        
        all_entries_for_machine = []

        # --- Loop backward in time, day by day ---
        for day in range(days_to_fetch):
            # Define the 24-hour window for the current day
            end_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=day)
            start_time = end_time - dt.timedelta(days=1)
            
            # Format timestamps correctly for the API
            start_iso = start_time.isoformat().replace('+00:00', 'Z')
            end_iso = end_time.isoformat().replace('+00:00', 'Z')
            
            print(f"Fetching data for {machine_name} | Day {day+1}/{days_to_fetch} | Window: {start_iso} to {end_iso}")

            try:
                # Make one API call for this 24-hour window
                response = api.get_status_periods(
                    start_time=start_iso, 
                    end_time=end_iso, 
                    machine_ids=machine_id,
                    page_size=1000 # Max out the page size to get all data for the day
                )
                
                if response and 'items' in response and response['items']:
                    all_entries_for_machine.extend(response['items'])
                
                # Be respectful to the API
                time.sleep(1)

            except Exception as e:
                print(f"An error occurred while fetching data for day {day+1}: {e}")
                continue # Skip to the next day if an error occurs

        # --- Process and Save all collected data for the machine ---
        if all_entries_for_machine:
            print(f"\nTotal entries fetched for machine {machine_name}: {len(all_entries_for_machine)}")
            
            machine_df = pd.DataFrame(all_entries_for_machine)
            processed_df = process_dataframe(machine_df)
            
            # Remove duplicate entries just in case of overlapping time windows
            processed_df.drop_duplicates(subset=['id'], inplace=True)
            
            file_name = f"machine_data_{machine_name.replace(' ', '_')}.csv"
            processed_df.to_csv(file_name, index=False)
            print(f"Successfully saved {len(processed_df)} unique entries to {file_name}")
        else:
            print(f"No data was successfully fetched for machine {machine_name}.")

if __name__ == "__main__":
    main()
