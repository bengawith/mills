import time
import pandas as pd
import os
import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import httpx

# Assuming your models are now in database_models
from database import engine, Base
import database_models
from fourjaw.api import FourJaw
from fourjaw.data_processor import DataProcessor
from const.config import Config

# --- Database Setup ---
# Create all tables defined in database_models if they don't exist
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- MQTT Ingestion Logic ---

def on_connect(client, userdata, flags, rc):
    """Callback for when the client connects to the MQTT broker."""
    if rc == 0:
        print(f"[{datetime.now()}] MQTT Ingestor: Connected to Broker!")
        client.subscribe(Config.MQTT_TOPIC)
        print(f"[{datetime.now()}] MQTT Ingestor: Subscribed to topic '{Config.MQTT_TOPIC}'")
    else:
        print(f"[{datetime.now()}] MQTT Ingestor: Failed to connect, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback for when a message is received from the broker."""
    print(f"[{datetime.now()}] MQTT Ingestor: Received message on topic {msg.topic}")
    db = SessionLocal()
    try:
        payload = json.loads(msg.payload.decode())
        
        cut_event = database_models.CutEvent(
            machine_id=payload.get("machine_id"),
            timestamp_utc=payload.get("timestamp_utc"),
            cut_count=payload.get("cut_count")
        )
        db.add(cut_event)
        db.commit()
        print(f"[{datetime.now()}] MQTT Ingestor: Successfully saved cut event for machine {payload.get('machine_id')}.")
    except json.JSONDecodeError:
        print(f"[{datetime.now()}] MQTT Ingestor: Error - Could not decode JSON payload.")
    except Exception as e:
        print(f"[{datetime.now()}] MQTT Ingestor: Error processing message: {e}")
    finally:
        db.close()

def setup_mqtt_client():
    """Sets up and connects the MQTT client."""
    client = mqtt.Client(client_id=f"mill-dash-ingestor-{int(time.time())}")
    # client.username_pw_set(Config.MQTT_USER, Config.MQTT_PASSWORD) # Uncomment if auth is needed
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT)
        return client
    except Exception as e:
        print(f"[{datetime.now()}] MQTT Ingestor: Error connecting to MQTT broker: {e}")
        return None

# --- FourJaw API Polling Logic (Your existing logic, slightly refactored) ---

def sort_and_save_csv():
    """
    Reads a CSV file, sorts it by the 'start_timestamp' column, and overwrites the original file.
    """
    for file_name in os.listdir("data"):
        if not file_name.endswith(".csv") or not file_name.startswith("mill_"):
            continue
        file_path = os.path.join("data", file_name)
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
    db_session = SessionLocal()
    try:
        print(f"[{datetime.now()}] Processing data in ingest_data...")
        # Convert timestamp columns to datetime objects
        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='mixed', utc=True)
        df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], format='mixed', utc=True)

        processor = DataProcessor()
        processed_df = processor.process_data(df)

        print(f"[{datetime.now()}] Inserting data into the database...")
        try:
            existing_ids = pd.read_sql('SELECT id FROM historical_machine_data', engine)['id'].tolist()
            # Remove duplicates within the current DataFrame based on 'id'
            processed_df.drop_duplicates(subset=['id'], inplace=True)
            # Filter out records that already exist in the database
            processed_df = processed_df[~processed_df['id'].isin(existing_ids)]
            processed_df.to_sql('historical_machine_data', engine, if_exists='append', index=False)
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


def get_latest_timestamp_from_db(db_session, machine_id: str) -> datetime | None:
    """Queries for the latest end_timestamp for a given machine_id."""
    latest = db_session.query(database_models.HistoricalMachineData.end_timestamp)\
                       .filter(database_models.HistoricalMachineData.machine_id == machine_id)\
                       .order_by(database_models.HistoricalMachineData.end_timestamp.desc())\
                       .first()
    return latest[0] if latest else None


def ingest_dataframe_to_db(df: pd.DataFrame, db):
    """Ingests a processed DataFrame into the database, handling duplicates."""
    if df.empty:
        print(f"[{datetime.now()}] FourJaw Ingestor: No new data to ingest.")
        return

    try:
        # Get existing IDs from the DB to prevent duplicates
        existing_ids = pd.read_sql(f"SELECT id FROM {database_models.HistoricalMachineData.__tablename__}", engine)['id'].tolist()
        
        new_records_df = df[~df['id'].isin(existing_ids)]
        
        if not new_records_df.empty:
            new_records_df.to_sql(database_models.HistoricalMachineData.__tablename__, engine, if_exists='append', index=False)
            print(f"[{datetime.now()}] FourJaw Ingestor: Ingestion complete. Inserted {len(new_records_df)} new records.")
        else:
            print(f"[{datetime.now()}] FourJaw Ingestor: No new unique records to insert.")

    except Exception as e:
        print(f"[{datetime.now()}] FourJaw Ingestor: Error inserting data into the database: {e}")


def fetch_and_process_fourjaw_data():
    """Fetches new data from the FourJaw API since the last recorded entry."""
    print(f"[{datetime.now()}] FourJaw Ingestor: Starting API data ingestion job...")
    fourjaw_api = FourJaw()
    processor = DataProcessor()
    db = SessionLocal()

    try:
        for machine_id in Config.MACHINE_IDS:
            machine_name = Config.MACHINE_ID_MAP.get(machine_id, machine_id)
            print(f"\n--- Checking for new data for machine: {machine_name} ---")
            
            latest_db_timestamp = get_latest_timestamp_from_db(db, machine_id)
            
            if latest_db_timestamp:
                start_time = latest_db_timestamp + timedelta(seconds=1)
            else:
                # Fallback: If no data exists, fetch the last N days
                start_time = datetime.now(timezone.utc) - timedelta(days=Config.FOURJAW_HISTORICAL_FETCH_DAYS)
            
            end_time = datetime.now(timezone.utc)
            
            print(f"Fetching data from {start_time.isoformat()} to {end_time.isoformat()}")

            # Using the rolling time-window fetch logic
            all_entries = []
            current_window_end = end_time
            while current_window_end > start_time:
                window_start = max(start_time, current_window_end - timedelta(days=1))
                
                start_iso = window_start.isoformat().replace('+00:00', 'Z')
                end_iso = current_window_end.isoformat().replace('+00:00', 'Z')

                try:
                    response = fourjaw_api.get_status_periods(
                        start_time=start_iso, end_time=end_iso, machine_ids=machine_id
                    )
                    if response and 'items' in response and response['items']:
                        all_entries.extend(response['items'])
                    time.sleep(1)
                except Exception as e:
                    print(f"An error occurred during API fetch: {e}")

                current_window_end = window_start

            if all_entries:
                new_data_df = pd.DataFrame(all_entries)
                processed_df = processor.process_data(new_data_df)
                ingest_dataframe_to_db(processed_df, db)
            else:
                print(f"No new entries found for machine {machine_name}.")
    finally:
        db.close()

# --- Main Execution Block ---
if __name__ == "__main__":
    # Ingest CSV to begin
    ingest_csv_data()

    # Start the MQTT client in a non-blocking background thread
    mqtt_client = setup_mqtt_client()
    if mqtt_client:
        mqtt_client.loop_start()

    # Run the FourJaw polling loop indefinitely
    while True:
        fetch_and_process_fourjaw_data()
        print(f"\n[{datetime.now()}] FourJaw Polling complete. Waiting {Config.FOURJAW_POLLING_INTERVAL_SECONDS} seconds for next run...")
        time.sleep(Config.FOURJAW_POLLING_INTERVAL_SECONDS)
        sort_and_save_csv()