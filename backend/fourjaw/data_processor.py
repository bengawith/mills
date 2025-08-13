from dataclasses import dataclass, field
from typing import List
import pandas as pd
from .api import FourJaw
from const import Config
import datetime as dt
pd.set_option('display.max_columns', None)


@dataclass
class DataProcessorConfig:
    """
    Configuration for the DataProcessor class.
    """
    client: FourJaw = FourJaw()
    start_time: str = dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')
    end_time: str = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat().replace('+00:00', 'Z')
    page_size: int = 1000
    page: int = 1
    machine_ids: List[str] = field(default_factory=lambda: Config.MACHINE_IDS)



class DataProcessor:
    def __init__(self, config: DataProcessorConfig = DataProcessorConfig(),):
        self.config = config
        self.api = config.client


    def get_shift_info(self, timestamp: pd.Timestamp) -> tuple:
        """
        Determines the shift and day of the week for a given timestamp.
        """
        day_name = timestamp.strftime('%A')
        current_time = timestamp.time()

        if Config.DAY_SHIFT_START <= current_time < Config.DAY_SHIFT_END:
            shift_name = "DAY"
        else:
            shift_name = "NIGHT"
            
        return shift_name, day_name.upper()

    def process_time_entries(self, start_time: str | None = None, end_time: str | None = None, page_size: int | None = None, page: int | None = None) -> pd.DataFrame:
        """
        Fetches and processes time entry data for a given period.
        """
        if start_time is not None:
            self.config.start_time = start_time
        if end_time is not None:
            self.config.end_time = end_time
        if page_size is not None:
            self.config.page_size = page_size
        if page is not None:
            self.config.page = page
        raw_entries = self.api.get_status_periods(start_time=self.config.start_time, end_time=self.config.end_time, machine_ids=Config.MACHINE_IDS, page_size=self.config.page_size, page=self.config.page)
        if not raw_entries or 'items' not in raw_entries or not raw_entries['items']:
            print("No time entries found for the specified period.")
            return pd.DataFrame()

        # Use the 'items' key from the paginated response
        df = pd.DataFrame(raw_entries['items'])

        # Add name of machine
        df.insert(0, 'name', df['machine_id'].copy().apply(lambda x: Config.MACHINE_ID_MAP[x]))
        
        # Use format='ISO8601' for flexible timestamp parsing
        # Handles timestamps with or without microseconds.
        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='ISO8601')
        df['end_timestamp'] = pd.to_datetime(df['end_timestamp'], format='ISO8601')
        
        # Calculate the duration of each entry in seconds
        df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()
        
        # Add shift and day information
        df['shift'], df['day_of_week'] = zip(*df['start_timestamp'].apply(self.get_shift_info))
        
        # Map statuses to our utilisation categories
        df['utilisation_category'] = df['productivity'].apply(lambda x: x.upper()) + " " + df['classification']
        
        return df

if __name__ == "__main__":
    def main():
        processor = DataProcessor()
        
        end_time = dt.datetime.now(dt.timezone.utc)
        start_time = end_time - dt.timedelta(days=100)
        
        start_iso = start_time.isoformat().replace('+00:00', 'Z')
        end_iso = end_time.isoformat().replace('+00:00', 'Z')
        
        print(f"Fetching data from {start_iso} to {end_iso}...")
        print(f"For machines: {Config.MACHINE_IDS[0]}")
        
        try:
            processed_data_df = processor.process_time_entries(start_time=start_iso, end_time=end_iso)

            if not processed_data_df.empty:
                print("\n--- Successfully Processed Data ---")
                # Let's select more relevant columns for the head() view
                '''
                print(processed_data_df[[
                    'machine_id', 'start_timestamp', 'end_timestamp', 
                    'duration_seconds', 'shift', 'utilisation_category'
                ]].head())
                '''
                print(processed_data_df.head())
                print(processed_data_df.tail())
                # Example Analysis: Calculate total time in each utilisation category
                category_summary = processed_data_df.groupby('utilisation_category')['duration_seconds'].sum() / 3600 # in hours
                print("\n--- Summary (Total Hours by Category) ---")
                print(category_summary)

        except Exception as e:
            print(f"\nAn error occurred: {e}")

    main()