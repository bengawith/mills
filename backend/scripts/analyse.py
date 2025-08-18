import pandas as pd
import os

dt_cats = set()
for file in os.listdir('data'):
    if file.startswith('mill_') and file.endswith('.csv'):
        df: pd.DataFrame = pd.read_csv(os.path.join('data', file), encoding='utf-8')
        downtime_categories = df['downtime_reason_name'].unique()
        dt_cats.update(downtime_categories)

print(dt_cats)
print(len(dt_cats))