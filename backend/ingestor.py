
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
    csv_files = ["mill_1.csv", "mill_2.csv", "mill_3.csv"]
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
    # Filter data between May 5th and August 15th
    start_date = datetime(2025, 5, 5, tzinfo=timezone.utc)
    end_date = datetime(2025, 8, 15, 17, 0, 0, tzinfo=timezone.utc)
    df = df[(df['start_timestamp'] >= start_date) & (df['end_timestamp'] <= end_date)]

    print(f"[{datetime.now()}] Ingesting data...")
    ingest_data(df)

def fetch_and_ingest_fourjaw_data():
    """
    Fetches data from the FourJaw API and ingests it into the database.
    """
    print(f"[{datetime.now()}] Starting FourJaw API data ingestion job...")
    
    # Determine the start date for fetching data from the API.
    # This will be August 15th, 2025.
    start_date = datetime(2025, 8, 15, 17, 0, 0, tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)

    # Loop through each machine
    for machine_id in Config.MACHINE_IDS:
        machine_name = Config.MACHINE_ID_MAP.get(machine_id, machine_id)

        # Only load data for mills
        if not machine_name.strip().lower().startswith('mill'):
            continue

        print(f"\n--- Starting data fetch for machine: {machine_name} ---")
        
        all_entries_for_machine = []

        # Loop backward in time, day by day
        current_day = end_date
        while current_day > start_date:
            # Define the 24-hour window for the current day
            window_end = current_day
            window_start = current_day - timedelta(days=1)
            
            # Format timestamps correctly for the API
            start_iso = window_start.isoformat().replace('+00:00', 'Z')
            end_iso = window_end.isoformat().replace('+00:00', 'Z')
            
            print(f"Fetching data for {machine_name} | Window: {start_iso} to {end_iso}")

            try:
                # Make one API call for this 24-hour window
                response = fourjaw_api.get_status_periods(
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
                print(f"An error occurred while fetching data: {e}")
                continue # Skip to the next day if an error occurs
            
            current_day -= timedelta(days=1)

        # --- Process and Save all collected data for the machine ---
        if all_entries_for_machine:
            print(f"\nTotal entries fetched for machine {machine_name}: {len(all_entries_for_machine)}")
            
            machine_df = pd.DataFrame(all_entries_for_machine)
            ingest_data(machine_df)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))
    
    # Ensure the database tables are created before starting ingestion
    Base.metadata.create_all(bind=engine)

    ingest_csv_data()
    fetch_and_ingest_fourjaw_data()
