import pandas as pd
import os
from const import Config


def sort_csv_by_date(file_path):
    """
    Reads a CSV file, sorts it by the 'timestamp' column, and overwrites the original file.
    """
    try:
        df = pd.read_csv(file_path)
        df['start_timestamp'] = pd.to_datetime(df['start_timestamp'], format='ISO8601')
        df_sorted = df.sort_values(by='start_timestamp')
        df_sorted.to_csv(file_path, index=False)
        print(f"Successfully sorted {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":

    
    csv_files = [
        os.path.join('data', f'mill_{config.MACHINE_IDS[0]}.csv'),
        os.path.join('data', f'mill_{config.MACHINE_IDS[1]}.csv'),
        os.path.join('data', f'mill_{config.MACHINE_IDS[2]}.csv')
    ]

    for csv_file in csv_files:
        sort_csv_by_date(csv_file)
