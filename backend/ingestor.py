import pandas as pd
import os
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database import engine, MillData, Base
from fourjaw.api import FourJaw
from fourjaw.data_processor import DataProcessor
from const.config import Config

# Initialize FourJaw API client
fourjaw_api = FourJaw()
# Create a session to interact with the database
Session = sessionmaker(bind=engine)

def ingest_csv_data():
    db_session = Session()
    try:
        print(f"[{datetime.now()}] Starting CSV data ingestion job...")
        data_dir = "/app/data"
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            print(f"Processing {file_path}...")
            df = pd.read_csv(file_path)

            for index, row in df.iterrows():
                data_entry = MillData(
                    id=row['id'],
                    name=row['name'],
                    machine_id=row['machine_id'],
                    downtime_reason_name=row['downtime_reason_name'],
                    start_timestamp=pd.to_datetime(row['start_timestamp']),
                    end_timestamp=pd.to_datetime(row['end_timestamp']),
                    productivity=row['productivity'],
                    classification=row['classification'],
                    duration_seconds=row['duration_seconds'],
                    shift=row['shift'],
                    day_of_week=row['day_of_week'],
                    utilisation_category=row['utilisation_category']
                )
                try:
                    db_session.add(data_entry)
                    db_session.commit()
                except IntegrityError:
                    db_session.rollback()
                    # print(f"Skipping duplicate entry: {data_entry.id}")
                except Exception as e:
                    db_session.rollback()
                    print(f"Error adding data entry {data_entry.id}: {e}")
        
        print(f"[{datetime.now()}] CSV data ingestion job completed.")

    except Exception as e:
        print(f"[{datetime.now()}] Error during CSV data ingestion: {e}")
    finally:
        db_session.close()

def ingest_fourjaw_data():
    # This function will remain for future FourJaw API integration
    # For now, it's a placeholder
    print("FourJaw API ingestion function (placeholder) called.")
    pass

def start_ingestor():
    scheduler = BackgroundScheduler()
    # Schedule the job to run every hour
    scheduler.add_job(ingest_fourjaw_data, 'interval', hours=1)
    scheduler.start()
    print("Ingestor scheduler started.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))
    
    # Ensure the database tables are created before starting ingestion
    Base.metadata.create_all(bind=engine)

    ingest_csv_data() # Run once immediately for CSV data
    # start_ingestor() # Commented out for now, as we are focusing on CSV ingestion

    # Keep the main thread alive for the scheduler to run (if enabled)
    try:
        pass
    except (KeyboardInterrupt, SystemExit):
        pass
