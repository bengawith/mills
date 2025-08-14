import os
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database import engine
from models import HistoricalMachineData
from fourjaw.api import FourJaw
from fourjaw.data_processor import DataProcessor
from const.config import Config

# Initialize FourJaw API client
fourjaw_api = FourJaw()
# Create a session to interact with the database
Session = sessionmaker(bind=engine)

def ingest_fourjaw_data():
    data_processor = DataProcessor()
    db_session = Session()
    try:
        print(f"[{datetime.now()}] Starting data ingestion job...")

        # Determine the time range for data fetching
        # Fetch data for the last hour to ensure no gaps and handle potential delays
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        start_time_iso = start_time.isoformat().replace("+00:00", "Z")
        end_time_iso = end_time.isoformat().replace("+00:00", "Z")

        # Fetch raw data from FourJaw API
        raw_data = fourjaw_api.get_status_periods(
            start_time=start_time_iso,
            end_time=end_time_iso,
            machine_ids=Config.MACHINE_IDS
        )

        # Process the raw data
        processed_data = data_processor.process_time_entries(None)

        # Insert processed data into the database
        for index, entry in processed_data.iterrows():
            # Convert dict to HistoricalMachineData model instance
            data_entry = HistoricalMachineData(
                id=entry['id'],
                name=entry['name'],
                machine_id=entry['machine_id'],
                downtime_reason_name=entry['downtime_reason_name'],
                start_timestamp=entry['start_timestamp'],
                end_timestamp=entry['end_timestamp'],
                productivity=entry['productivity'],
                classification=entry['classification'],
                duration_seconds=entry['duration_seconds'],
                shift=entry['shift'],
                day_of_week=entry['day_of_week'],
                utilisation_category=entry['utilisation_category']
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
        
        print(f"[{datetime.now()}] Data ingestion job completed. Processed {len(processed_data)} entries.")

    except Exception as e:
        print(f"[{datetime.now()}] Error during data ingestion: {e}")
    finally:
        db_session.close()

def start_ingestor():
    scheduler = BackgroundScheduler()
    # Schedule the job to run every hour
    scheduler.add_job(ingest_fourjaw_data, 'interval', hours=1)
    scheduler.start()
    print("Ingestor scheduler started.")

if __name__ == "__main__":
    # This part is for local testing of the ingestor script
    # In Docker, it will be run as part of the service
    from dotenv import load_dotenv
    load_dotenv(os.path.join(Config.ROOT_DIR, '.env'))
    
    # Ensure the database tables are created before starting ingestion
    from database import Base
    Base.metadata.create_all(bind=engine)

    ingest_fourjaw_data() # Run once immediately
    start_ingestor()

    # Keep the main thread alive for the scheduler to run
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
