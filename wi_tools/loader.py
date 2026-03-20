import pandas as pd
from pathlib import Path

FIELDS = ['image_id', 'deployment_id', 'timestamp', 'location', 'common_name']


def load_dataset(images_dir):
    parts = []
    for f in Path(images_dir).iterdir():
        if not f.is_file():
            continue

        parts.append(pd.read_csv(f.resolve(), low_memory=False))

    df = pd.concat(parts)
    df = df[FIELDS]
    df.dropna(subset=FIELDS, inplace=True)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"].str.split(" (", regex=False).str[0]
    ).dt.strftime("%Y-%m-%d_%H-%M-%S")

    df = df.sort_values(['deployment_id', 'image_id', 'timestamp'], ascending=True).reset_index(drop=True)

    return df
