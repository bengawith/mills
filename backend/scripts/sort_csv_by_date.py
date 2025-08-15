import pandas as pd
import os

def sort_csv_by_date(file_path):
    """
    Reads a CSV file, sorts it by the 'timestamp' column, and overwrites the original file.
    """
    try:
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['start_timestamp'], format='ISO8601')
        df_sorted = df.sort_values(by='timestamp')
        df_sorted.to_csv(file_path, index=False)
        print(f"Successfully sorted {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":

    
    csv_files = [
        os.path.join('data', 'mill_1.csv'),
        os.path.join('data', 'mill_2.csv'),
        os.path.join('data', 'mill_3.csv')
    ]

    for csv_file in csv_files:
        sort_csv_by_date(csv_file)
