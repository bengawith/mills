import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import pandas as pd
from const import Config


for file in os.listdir("data"):
    if file.endswith(".csv") and file.startswith("mill_"):
        df = pd.read_csv(os.path.join("data", file))
        df.insert(0, 'name', df['machine_id'].copy().apply(lambda x: config.MACHINE_ID_MAP.get(x, 'Unknown')))
        df.to_csv(os.path.join("data", file), index=False)
        print(f"Processed {file}")
print("All files processed.")
