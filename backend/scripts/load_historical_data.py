import pandas as pd
import os
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database import engine
from models import HistoricalMachineData # Assuming HistoricalMachineData is defined in models.py

# Define paths to your CSV files
# Assuming the script is run from the project root or backend directory
# Adjust paths as necessary
CSV_FILES = [
    "data/mill_1.csv",
    "data/mill_2.csv",
    "data/mill_3.csv",
]

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

def load_historical_data():
    for csv_file in CSV_FILES:
        print(f"Loading data from {csv_file}...")
        try:
            # Read CSV into a pandas DataFrame
            df = pd.read_csv(csv_file)

            # Iterate over DataFrame rows and insert into database
            for index, row in df.iterrows():
                # Convert timestamp strings to datetime objects with timezone
                start_timestamp = datetime.fromisoformat(row['start_timestamp'])
                end_timestamp = datetime.fromisoformat(row['end_timestamp'])

                # Create a HistoricalMachineData object
                data_entry = HistoricalMachineData(
                    id=row['id'],
                    name=row['name'],
                    machine_id=row['machine_id'],
                    downtime_reason_name=row['downtime_reason_name'],
                    start_timestamp=start_timestamp,
                    end_timestamp=end_timestamp,
                    productivity=row['productivity'],
                    classification=row['classification'],
                    duration_seconds=row['duration_seconds'],
                    shift=row['shift'],
                    day_of_week=row['day_of_week'],
                    utilisation_category=row['utilisation_category']
                )
                session.add(data_entry)
            
            session.commit()
            print(f"Successfully loaded data from {csv_file}.")

        except IntegrityError:
            session.rollback()
            print(f"Skipping duplicates in {csv_file}. Data already exists.")
        except Exception as e:
            session.rollback()
            print(f"Error loading data from {csv_file}: {e}")
    
    session.close()
    print("Historical data loading complete.")

if __name__ == "__main__":
    load_historical_data()
