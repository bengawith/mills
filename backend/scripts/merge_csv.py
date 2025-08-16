import pandas as pd
import os

panes: list[pd.DataFrame] = []
for file in os.listdir('data'):
    df: pd.DataFrame = pd.read_csv(os.path.join('data', file))
    panes.append(df)

df: pd.DataFrame = pd.concat(panes)
df.drop_duplicates(inplace=True)
df.to_csv('./data/mills.csv')
