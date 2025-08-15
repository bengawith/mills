import os
import pandas as pd


def main() -> None:
    for file in os.listdir('temp'):
        df_new: pd.DataFrame = pd.read_csv(os.path.join('temp', file))
        df_full: pd.DataFrame = pd.read_csv(os.path.join('data', file))

        frames = [df_full, df_new]
        df_full = pd.concat(frames)
        df_full.drop_duplicates(inplace=True)
        df_full.to_csv(os.path.join('data', file), index=False)


if __name__ == '__main__':
    main()