
import time
import pandas as pd
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import httpx

from database import engine, MillData, Base
from fourjaw.api import FourJaw
from fourjaw.data_processor import DataProcessor
from const.config import Config

# Initialize FourJaw API client
fourjaw_api = FourJaw()
# Create a session to interact with the database
Session: sessionmaker = sessionmaker(bind=engine)

def get_latest_timestamp_from_db(machine_id: str) -> datetime | None:
    """
    Queries the database for the latest end_timestamp for a given machine_id.
    """
    db_session = Session()
    try:
        latest_timestamp = db_session.query(MillData.end_timestamp)
        latest_timestamp = latest_timestamp.filter(MillData.machine_id == machine_id)
        latest_timestamp = latest_timestamp.order_by(MillData.end_timestamp.desc()).first()
        if latest_timestamp:
            return latest_timestamp[0]
        return None
    except Exception as e:
        print(f"Error fetching latest timestamp for machine {machine_id}: {e}")
        return None
    finally:
        db_session.close()

def sort_and_save_csv(file_path: str):
    """
    Reads a CSV file, sorts it by the 'start_timestamp' column, and overwrites the original file.
    """
    try:
        df = pd.read_csv(file_path)
        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='mixed', utc=True)
        df_sorted = df.sort_values(by='start_timestamp')
        df_sorted.to_csv(file_path, index=False)
        print(f"Successfully sorted and saved {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def ingest_data(df: pd.DataFrame):
    """
    Ingests a DataFrame into the database.
    """
    db_session = Session()
    try:
        print(f"[{datetime.now()}] Processing data in ingest_data...")
        # Convert timestamp columns to datetime objects
        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='mixed', utc=True)
        df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], format='mixed', utc=True)

        processor = DataProcessor()
        processed_df = processor.process_data(df)

        print(f"[{datetime.now()}] Inserting data into the database...")
        try:
            existing_ids = pd.read_sql('SELECT id FROM mill_data', engine)['id'].tolist()
            processed_df = processed_df[~processed_df['id'].isin(existing_ids)]
            processed_df.to_sql('mill_data', engine, if_exists='append', index=False)
            print(f"[{datetime.now()}] Ingestion job completed. Total unique records processed: {len(processed_df)}.")
        except Exception as e:
            print(f"[{datetime.now()}] Error inserting data into the database: {e}")

    except Exception as e:
        print(f"[{datetime.now()}] Critical error during data ingestion: {e}")
    finally:
        db_session.close()

def ingest_csv_data():
    """
    Ingests data from the mill CSV files into the database.
    """
    print(f"[{datetime.now()}] Starting CSV data ingestion job...")
    csv_files = [f for f in os.listdir("data") if f.startswith("mill_") and f.endswith(".csv")]
    data_frames = []
    print(f"[{datetime.now()}] Reading CSV files...")
    for file in csv_files:
        df = pd.read_csv(os.path.join("data", file))
        data_frames.append(df)
    
    print(f"[{datetime.now()}] Concatenating DataFrames...")
    df = pd.concat(data_frames, ignore_index=True)
    
    print(f"[{datetime.now()}] Converting timestamps...")
    # Convert timestamp columns to datetime objects
    df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='mixed', utc=True)
    df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], format='mixed', utc=True)

    print(f"[{datetime.now()}] Filtering dates...")

    print(f"[{datetime.now()}] Ingesting data...")
    ingest_data(df)

def fetch_and_ingest_fourjaw_data():
    """
    Fetches data from the FourJaw API and ingests it into the database.
    """
    print(f"[{datetime.now()}] Starting FourJaw API data ingestion job...")
    
    end_date = datetime.now(timezone.utc)

    # Loop through each machine
    for machine_id in Config.MACHINE_IDS:
        machine_name = Config.MACHINE_ID_MAP.get(machine_id, machine_id)

        # Only load data for mills
        if not machine_name.strip().lower().startswith('mill'):
            continue

        print(f"\n--- Starting data fetch for machine: {machine_name} ---")
        
        # Determine the start date dynamically from the database
        latest_db_timestamp = get_latest_timestamp_from_db(machine_id)
        if latest_db_timestamp:
            # Fetch data from 1 second after the latest entry in DB
            api_fetch_start_date = latest_db_timestamp + timedelta(seconds=1)
            print(f"Latest timestamp in DB for {machine_name}: {latest_db_timestamp}. Fetching from {api_fetch_start_date}")
        else:
            # If no data in DB, fetch from a default historical date (e.g., start of 2025)
            # Or, if you want to rely purely on CSV, you could read the CSV here to find its latest timestamp
            api_fetch_start_date = datetime(2025, 5, 5, 0, 0, 0, tzinfo=timezone.utc) # Default if no data in DB
            print(f"No data found in DB for {machine_name}. Fetching from default start date: {api_fetch_start_date}")

        all_entries_for_machine = []

        # Loop backward in time, day by day, from end_date down to api_fetch_start_date
        current_day_window_end = end_date
        while current_day_window_end > api_fetch_start_date:
            window_start = max(api_fetch_start_date, current_day_window_end - timedelta(days=1))
            window_end = current_day_window_end
            
            # Format timestamps correctly for the API
            start_iso = window_start.isoformat().replace('+00:00', 'Z')
            end_iso = window_end.isoformat().replace('+00:00', 'Z')
            
            print(f"Fetching data for {machine_name} | Window: {start_iso} to {end_iso}")

            try:
                response = fourjaw_api.get_status_periods(
                    start_time=start_iso, 
                    end_time=end_iso, 
                    machine_ids=machine_id,
                    page_size=1000 # Max out the page size to get all data for the day
                )
                
                if response and 'items' in response and response['items']:
                    all_entries_for_machine.extend(response['items'])
                
                time.sleep(1) # Be respectful to the API

            except Exception as e:
                print(f"An error occurred while fetching data: {e}")
                # Continue to the next day/window even if an error occurs for one
            
            current_day_window_end = window_start # Move to the start of the current window for the next iteration

        # --- Process and Save all collected data for the machine ---
        if all_entries_for_machine:
            print(f"\nTotal new entries fetched for machine {machine_name}: {len(all_entries_for_machine)}")
            dp: DataProcessor = DataProcessor()

            new_data_df: pd.DataFrame = dp.process_data(pd.DataFrame(all_entries_for_machine))
                        
            # Append to CSV and re-sort
            csv_file_name = f"mill_{machine_id}.csv" # Assuming machine_id maps directly to CSV name
            csv_file_path = os.path.join("data", csv_file_name)

            if os.path.exists(csv_file_path):
                # Read existing CSV, append new data, and save
                existing_df = pd.read_csv(csv_file_path)
                combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
                # Drop duplicates based on start_timestamp if they are in both the API and CSV
                combined_df.drop_duplicates(subset=['start_timestamp'], inplace=True)
                combined_df.to_csv(csv_file_path, index=False)
                print(f"Appended {len(new_data_df)} new entries to {csv_file_path}")
            else:
                # If CSV doesn't exist, just save the new data
                new_data_df.to_csv(csv_file_path, index=False)
                print(f"Created {csv_file_path} with {len(new_data_df)} entries.")
            
            # Ensure the CSV is sorted after appending
            sort_and_save_csv(csv_file_path)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))
    
    # Ensure the database tables are created before starting ingestion
    Base.metadata.create_all(bind=engine)

    # First, load current CSV data
    ingest_csv_data()
    # First, fetch and update CSVs with latest API data
    fetch_and_ingest_fourjaw_data()
    # Then, ingest all CSV data (including newly appended) into the database
    ingest_csv_data()
