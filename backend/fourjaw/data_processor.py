from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd
from const import Config
import datetime as dt
from sqlalchemy.orm import Session
from database import MillData, SessionLocal
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
pd.set_option('display.max_columns', None)


@dataclass
class DataProcessorConfig:
    """
    Configuration for the DataProcessor class.
    """
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    machine_ids: List[str] = field(default_factory=lambda: Config.MACHINE_IDS)


class DataProcessor:
    def __init__(self, config: DataProcessorConfig = DataProcessorConfig()):
        self.config = config

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

    def get_data_from_db(self, db: Session, start_time: Optional[dt.datetime] = None, end_time: Optional[dt.datetime] = None, machine_ids: Optional[List[str]] = None) -> pd.DataFrame:
        logger.info(f"Fetching data from DB with start_time={start_time}, end_time={end_time}, machine_ids={machine_ids}")
        query = db.query(MillData)

        if start_time:
            query = query.filter(MillData.start_timestamp >= start_time)
        if end_time:
            query = query.filter(MillData.end_timestamp <= end_time)
        if machine_ids:
            query = query.filter(MillData.machine_id.in_(machine_ids))

        data = query.all()
        logger.info(f"Fetched {len(data)} records from DB.")
        
        if not data:
            logger.info("No data fetched from DB.")
            return pd.DataFrame()

        df = pd.DataFrame([item.__dict__ for item in data])
        
        # Drop the SQLAlchemy internal state
        if '_sa_instance_state' in df.columns:
            df = df.drop(columns=['_sa_instance_state'])

        # Ensure timestamp columns are datetime objects
        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'])
        df['end_timestamp'] = pd.to_datetime(df['end_timestamp'])

        logger.info(f"DataFrame after get_data_from_db: {df.head()}")
        return df

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Processing data. Input DataFrame shape: {df.shape}")
        if df.empty:
            logger.info("Input DataFrame is empty in process_data.")
            return pd.DataFrame()

        # Calculate the duration of each entry in seconds
        df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()
        
        # Add shift and day information
        df['shift'], df['day_of_week'] = zip(*df['start_timestamp'].apply(self.get_shift_info))
        
        # Map statuses to our utilisation categories
        df['utilisation_category'] = df['productivity'].apply(lambda x: x.upper()) + " " + df['classification']
        
        logger.info(f"DataFrame after process_data: {df.head()}")
        return df

    def calculate_oee(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating OEE. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            # Assuming 'productive' classification means running and producing good parts
            # Availability: Uptime / (Uptime + Downtime)
            total_time = df['duration_seconds'].sum()
            if total_time == 0:
                logger.info("Total time is 0 in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            uptime_df = df[df['classification'] == 'UPTIME']
            total_uptime = uptime_df['duration_seconds'].sum()
            
            availability = total_uptime / total_time if total_time > 0 else 0

            # Performance: (Actual Production Rate / Ideal Production Rate)
            # This requires more context, like number of parts produced.
            # For now, we can approximate based on productive time vs total productive time
            # or assume 'productive' classification implies ideal performance.
            # Let's simplify for now: assume performance is 1 if productive, else 0.
            # A more accurate OEE would need actual production counts.
            # For this exercise, we'll assume performance is tied to productive uptime.
            # If 'productive' means producing, then performance is implicitly handled by availability.
            # Let's make a placeholder for now.
            performance = 1.0 # Placeholder, needs actual production data

            # Quality: (Good Parts / Total Parts)
            # Also requires more context. Placeholder for now.
            quality = 1.0 # Placeholder, needs actual quality data

            oee = availability * performance * quality
            
            result = {
                "oee": round(oee * 100, 2),
                "availability": round(availability * 100, 2),
                "performance": round(performance * 100, 2),
                "quality": round(quality * 100, 2)
            }
            logger.info(f"OEE calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_oee: {e}")
            raise # Re-raise the exception after logging

    def calculate_utilization(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating utilization. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_utilization.")
                return {"total_time_seconds": 0, "productive_uptime_seconds": 0, "unproductive_downtime_seconds": 0, "productive_downtime_seconds": 0, "utilization_percentage": 0}

            total_time_seconds = df['duration_seconds'].sum()
            productive_uptime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'UPTIME')]['duration_seconds'].sum()
            unproductive_downtime_seconds = df[(df['productivity'] == 'unproductive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()
            productive_downtime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()

            utilization_percentage = (productive_uptime_seconds / total_time_seconds) * 100 if total_time_seconds > 0 else 0

            result = {
                "total_time_seconds": round(total_time_seconds, 2),
                "productive_uptime_seconds": round(productive_uptime_seconds, 2),
                "unproductive_downtime_seconds": round(unproductive_downtime_seconds, 2),
                "productive_downtime_seconds": round(productive_downtime_seconds, 2),
                "utilization_percentage": round(utilization_percentage, 2)
            }
            logger.info(f"Utilization calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_utilization: {e}")
            raise # Re-raise the exception after logging

    def analyze_downtime(self, df: pd.DataFrame, excessive_downtime_threshold_seconds: int = 3600) -> dict:
        logger.info(f"Analyzing downtime. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in analyze_downtime.")
                return {"excessive_downtimes": [], "recurring_downtime_reasons": {}}

            downtime_df = df[df['classification'] == 'DOWNTIME']

            # Excessive Downtimes
            excessive_downtimes = downtime_df[downtime_df['duration_seconds'] > excessive_downtime_threshold_seconds]
            excessive_downtimes_list = excessive_downtimes[['name', 'machine_id', 'downtime_reason_name', 'duration_seconds', 'start_timestamp', 'end_timestamp']].to_dict(orient='records')

            # Recurring Downtime Reasons
            recurring_downtime_reasons = downtime_df.groupby('downtime_reason_name')['duration_seconds'].sum().sort_values(ascending=False).to_dict()

            result = {
                "excessive_downtimes": excessive_downtimes_list,
                "recurring_downtime_reasons": recurring_downtime_reasons
            }
            logger.info(f"Downtime analysis calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in analyze_downtime: {e}")
            raise # Re-raise the exception after logging

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Processing data. Input DataFrame shape: {df.shape}")
        if df.empty:
            logger.info("Input DataFrame is empty in process_data.")
            return pd.DataFrame()

        # Calculate the duration of each entry in seconds
        df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()
        
        # Add shift and day information
        df['shift'], df['day_of_week'] = zip(*df['start_timestamp'].apply(self.get_shift_info))
        
        # Map statuses to our utilisation categories
        df['utilisation_category'] = df['productivity'].apply(lambda x: x.upper()) + " " + df['classification']
        
        logger.info(f"DataFrame after process_data: {df.head()}")
        return df

    def calculate_oee(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating OEE. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            # Assuming 'productive' classification means running and producing good parts
            # Availability: Uptime / (Uptime + Downtime)
            total_time = df['duration_seconds'].sum()
            if total_time == 0:
                logger.info("Total time is 0 in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            uptime_df = df[df['classification'] == 'UPTIME']
            total_uptime = uptime_df['duration_seconds'].sum()
            
            availability = total_uptime / total_time if total_time > 0 else 0

            # Performance: (Actual Production Rate / Ideal Production Rate)
            # This requires more context, like number of parts produced.
            # For now, we can approximate based on productive time vs total productive time
            # or assume 'productive' classification implies ideal performance.
            # Let's simplify for now: assume performance is 1 if productive, else 0.
            # A more accurate OEE would need actual production counts.
            # For this exercise, we'll assume performance is tied to productive uptime.
            # If 'productive' means producing, then performance is implicitly handled by availability.
            # Let's make a placeholder for now.
            performance = 1.0 # Placeholder, needs actual production data

            # Quality: (Good Parts / Total Parts)
            # Also requires more context. Placeholder for now.
            quality = 1.0 # Placeholder, needs actual quality data

            oee = availability * performance * quality
            
            result = {
                "oee": round(oee * 100, 2),
                "availability": round(availability * 100, 2),
                "performance": round(performance * 100, 2),
                "quality": round(quality * 100, 2)
            }
            logger.info(f"OEE calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_oee: {e}")
            raise # Re-raise the exception after logging

    def calculate_utilization(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating utilization. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_utilization.")
                return {"total_time_seconds": 0, "productive_uptime_seconds": 0, "unproductive_downtime_seconds": 0, "productive_downtime_seconds": 0, "utilization_percentage": 0}

            total_time_seconds = df['duration_seconds'].sum()
            productive_uptime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'UPTIME')]['duration_seconds'].sum()
            unproductive_downtime_seconds = df[(df['productivity'] == 'unproductive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()
            productive_downtime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()

            utilization_percentage = (productive_uptime_seconds / total_time_seconds) * 100 if total_time_seconds > 0 else 0

            result = {
                "total_time_seconds": round(total_time_seconds, 2),
                "productive_uptime_seconds": round(productive_uptime_seconds, 2),
                "unproductive_downtime_seconds": round(unproductive_downtime_seconds, 2),
                "productive_downtime_seconds": round(productive_downtime_seconds, 2),
                "utilization_percentage": round(utilization_percentage, 2)
            }
            logger.info(f"Utilization calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_utilization: {e}")
            raise # Re-raise the exception after logging

    def analyze_downtime(self, df: pd.DataFrame, excessive_downtime_threshold_seconds: int = 3600) -> dict:
        logger.info(f"Analyzing downtime. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in analyze_downtime.")
                return {"excessive_downtimes": [], "recurring_downtime_reasons": {}}

            downtime_df = df[df['classification'] == 'DOWNTIME']

            # Excessive Downtimes
            excessive_downtimes = downtime_df[downtime_df['duration_seconds'] > excessive_downtime_threshold_seconds]
            excessive_downtimes_list = excessive_downtimes[['name', 'machine_id', 'downtime_reason_name', 'duration_seconds', 'start_timestamp', 'end_timestamp']].to_dict(orient='records')

            # Recurring Downtime Reasons
            recurring_downtime_reasons = downtime_df.groupby('downtime_reason_name')['duration_seconds'].sum().sort_values(ascending=False).to_dict()

            result = {
                "excessive_downtimes": excessive_downtimes_list,
                "recurring_downtime_reasons": recurring_downtime_reasons
            }
            logger.info(f"Downtime analysis calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in analyze_downtime: {e}")
            raise # Re-raise the exception after logging

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Processing data. Input DataFrame shape: {df.shape}")
        if df.empty:
            logger.info("Input DataFrame is empty in process_data.")
            return pd.DataFrame()

        # Calculate the duration of each entry in seconds
        df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()
        
        # Add shift and day information
        df['shift'], df['day_of_week'] = zip(*df['start_timestamp'].apply(self.get_shift_info))
        
        # Map statuses to our utilisation categories
        df['utilisation_category'] = df['productivity'].apply(lambda x: x.upper()) + " " + df['classification']
        
        logger.info(f"DataFrame after process_data: {df.head()}")
        return df

    def calculate_oee(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating OEE. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            # Assuming 'productive' classification means running and producing good parts
            # Availability: Uptime / (Uptime + Downtime)
            total_time = df['duration_seconds'].sum()
            if total_time == 0:
                logger.info("Total time is 0 in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            uptime_df = df[df['classification'] == 'UPTIME']
            total_uptime = uptime_df['duration_seconds'].sum()
            
            availability = total_uptime / total_time if total_time > 0 else 0

            # Performance: (Actual Production Rate / Ideal Production Rate)
            # This requires more context, like number of parts produced.
            # For now, we can approximate based on productive time vs total productive time
            # or assume 'productive' classification implies ideal performance.
            # Let's simplify for now: assume performance is 1 if productive, else 0.
            # A more accurate OEE would need actual production counts.
            # For this exercise, we'll assume performance is tied to productive uptime.
            # If 'productive' means producing, then performance is implicitly handled by availability.
            # Let's make a placeholder for now.
            performance = 1.0 # Placeholder, needs actual production data

            # Quality: (Good Parts / Total Parts)
            # Also requires more context. Placeholder for now.
            quality = 1.0 # Placeholder, needs actual quality data

            oee = availability * performance * quality
            
            result = {
                "oee": round(oee * 100, 2),
                "availability": round(availability * 100, 2),
                "performance": round(performance * 100, 2),
                "quality": round(quality * 100, 2)
            }
            logger.info(f"OEE calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_oee: {e}")
            raise # Re-raise the exception after logging

    def calculate_utilization(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating utilization. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_utilization.")
                return {"total_time_seconds": 0, "productive_uptime_seconds": 0, "unproductive_downtime_seconds": 0, "productive_downtime_seconds": 0, "utilization_percentage": 0}

            total_time_seconds = df['duration_seconds'].sum()
            productive_uptime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'UPTIME')]['duration_seconds'].sum()
            unproductive_downtime_seconds = df[(df['productivity'] == 'unproductive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()
            productive_downtime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()

            utilization_percentage = (productive_uptime_seconds / total_time_seconds) * 100 if total_time_seconds > 0 else 0

            result = {
                "total_time_seconds": round(total_time_seconds, 2),
                "productive_uptime_seconds": round(productive_uptime_seconds, 2),
                "unproductive_downtime_seconds": round(unproductive_downtime_seconds, 2),
                "productive_downtime_seconds": round(productive_downtime_seconds, 2),
                "utilization_percentage": round(utilization_percentage, 2)
            }
            logger.info(f"Utilization calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_utilization: {e}")
            raise # Re-raise the exception after logging

    def analyze_downtime(self, df: pd.DataFrame, excessive_downtime_threshold_seconds: int = 3600) -> dict:
        logger.info(f"Analyzing downtime. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in analyze_downtime.")
                return {"excessive_downtimes": [], "recurring_downtime_reasons": {}}

            downtime_df = df[df['classification'] == 'DOWNTIME']

            # Excessive Downtimes
            excessive_downtimes = downtime_df[downtime_df['duration_seconds'] > excessive_downtime_threshold_seconds]
            excessive_downtimes_list = excessive_downtimes[['name', 'machine_id', 'downtime_reason_name', 'duration_seconds', 'start_timestamp', 'end_timestamp']].to_dict(orient='records')

            # Recurring Downtime Reasons
            recurring_downtime_reasons = downtime_df.groupby('downtime_reason_name')['duration_seconds'].sum().sort_values(ascending=False).to_dict()

            result = {
                "excessive_downtimes": excessive_downtimes_list,
                "recurring_downtime_reasons": recurring_downtime_reasons
            }
            logger.info(f"Downtime analysis calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in analyze_downtime: {e}")
            raise # Re-raise the exception after logging

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info(f"Processing data. Input DataFrame shape: {df.shape}")
        if df.empty:
            logger.info("Input DataFrame is empty in process_data.")
            return pd.DataFrame()

        # Calculate the duration of each entry in seconds
        df['duration_seconds'] = (df['end_timestamp'] - df['start_timestamp']).dt.total_seconds()
        
        # Add shift and day information
        df['shift'], df['day_of_week'] = zip(*df['start_timestamp'].apply(self.get_shift_info))
        
        # Map statuses to our utilisation categories
        df['utilisation_category'] = df['productivity'].apply(lambda x: x.upper()) + " " + df['classification']
        
        logger.info(f"DataFrame after process_data: {df.head()}")
        return df

    def calculate_oee(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating OEE. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            # Assuming 'productive' classification means running and producing good parts
            # Availability: Uptime / (Uptime + Downtime)
            total_time = df['duration_seconds'].sum()
            if total_time == 0:
                logger.info("Total time is 0 in calculate_oee.")
                return {"oee": 0, "availability": 0, "performance": 0, "quality": 0}

            uptime_df = df[df['classification'] == 'UPTIME']
            total_uptime = uptime_df['duration_seconds'].sum()
            
            availability = total_uptime / total_time if total_time > 0 else 0

            # Performance: (Actual Production Rate / Ideal Production Rate)
            # This requires more context, like number of parts produced.
            # For now, we can approximate based on productive time vs total productive time
            # or assume 'productive' classification implies ideal performance.
            # Let's simplify for now: assume performance is 1 if productive, else 0.
            # A more accurate OEE would need actual production counts.
            # For this exercise, we'll assume performance is tied to productive uptime.
            # If 'productive' means producing, then performance is implicitly handled by availability.
            # Let's make a placeholder for now.
            performance = 1.0 # Placeholder, needs actual production data

            # Quality: (Good Parts / Total Parts)
            # Also requires more context. Placeholder for now.
            quality = 1.0 # Placeholder, needs actual quality data

            oee = availability * performance * quality
            
            result = {
                "oee": round(oee * 100, 2),
                "availability": round(availability * 100, 2),
                "performance": round(performance * 100, 2),
                "quality": round(quality * 100, 2)
            }
            logger.info(f"OEE calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_oee: {e}")
            raise # Re-raise the exception after logging

    def calculate_utilization(self, df: pd.DataFrame) -> dict:
        logger.info(f"Calculating utilization. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in calculate_utilization.")
                return {"total_time_seconds": 0, "productive_uptime_seconds": 0, "unproductive_downtime_seconds": 0, "productive_downtime_seconds": 0, "utilization_percentage": 0}

            total_time_seconds = df['duration_seconds'].sum()
            productive_uptime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'UPTIME')]['duration_seconds'].sum()
            unproductive_downtime_seconds = df[(df['productivity'] == 'unproductive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()
            productive_downtime_seconds = df[(df['productivity'] == 'productive') & (df['classification'] == 'DOWNTIME')]['duration_seconds'].sum()

            utilization_percentage = (productive_uptime_seconds / total_time_seconds) * 100 if total_time_seconds > 0 else 0

            result = {
                "total_time_seconds": round(total_time_seconds, 2),
                "productive_uptime_seconds": round(productive_uptime_seconds, 2),
                "unproductive_downtime_seconds": round(unproductive_downtime_seconds, 2),
                "productive_downtime_seconds": round(productive_downtime_seconds, 2),
                "utilization_percentage": round(utilization_percentage, 2)
            }
            logger.info(f"Utilization calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in calculate_utilization: {e}")
            raise # Re-raise the exception after logging

    def analyze_downtime(self, df: pd.DataFrame, excessive_downtime_threshold_seconds: int = 3600) -> dict:
        logger.info(f"Analyzing downtime. Input DataFrame shape: {df.shape}")
        try:
            if df.empty:
                logger.info("Input DataFrame is empty in analyze_downtime.")
                return {"excessive_downtimes": [], "recurring_downtime_reasons": {}}

            downtime_df = df[df['classification'] == 'DOWNTIME']

            # Excessive Downtimes
            excessive_downtimes = downtime_df[downtime_df['duration_seconds'] > excessive_downtime_threshold_seconds]
            excessive_downtimes_list = excessive_downtimes[['name', 'machine_id', 'downtime_reason_name', 'duration_seconds', 'start_timestamp', 'end_timestamp']].to_dict(orient='records')

            # Recurring Downtime Reasons
            recurring_downtime_reasons = downtime_df.groupby('downtime_reason_name')['duration_seconds'].sum().sort_values(ascending=False).to_dict()

            result = {
                "excessive_downtimes": excessive_downtimes_list,
                "recurring_downtime_reasons": recurring_downtime_reasons
            }
            logger.info(f"Downtime analysis calculated: {result}")
            return result
        except Exception as e:
            logger.exception(f"Error in analyze_downtime: {e}")
            raise # Re-raise the exception after logging

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
            # Use get_data_from_db and process_data
            with SessionLocal() as db:
                df = processor.get_data_from_db(db, start_iso, end_iso, Config.MACHINE_IDS)
                processed_data_df = processor.process_data(df)

            if not processed_data_df.empty:
                print("\n--- Successfully Processed Data ---")
                print(processed_data_df.head())
                print(processed_data_df.tail())
                
                # Example Analysis: Calculate total time in each utilisation category
                category_summary = processed_data_df.groupby('utilisation_category')['duration_seconds'].sum() / 3600 # in hours
                print("\n--- Summary (Total Hours by Category) ---")
                print(category_summary)

                # Test OEE
                oee_result = processor.calculate_oee(processed_data_df)
                print("\n--- OEE Result ---")
                print(oee_result)

                # Test Utilization
                utilization_result = processor.calculate_utilization(processed_data_df)
                print("\n--- Utilization Result ---")
                print(utilization_result)

                # Test Downtime Analysis
                downtime_result = processor.analyze_downtime(processed_data_df)
                print("\n--- Downtime Analysis Result ---")
                print(downtime_result)

        except Exception as e:
            print(f"\nAn error occurred: {e}")

    main()
