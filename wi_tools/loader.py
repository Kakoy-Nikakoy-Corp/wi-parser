import pandas as pd
from pathlib import Path

FIELDS = ['image_id', 'deployment_id', 'timestamp', 'location', 'common_name']


def load_dataset(images_dir: str) -> pd.DataFrame:
    # Collect dataframe from separate parts
    # if the dataset is scattered across multiple files
    parts: list[pd.DataFrame] = []
    for f in Path(images_dir).iterdir():
        if not f.is_file():
            continue

        parts.append(pd.read_csv(f.resolve(), low_memory=False))

    df: pd.DataFrame = pd.concat(parts)
    df = df[FIELDS].dropna()

    # Fix timestamp format for later use
    df["timestamp"] = pd.to_datetime(
        df["timestamp"].str.split(" (", regex=False).str[0]
    ).dt.strftime("%Y-%m-%d_%H-%M-%S")

    # Sort collected dataset in order to ensure script determinism
    df = df.sort_values(['deployment_id', 'image_id'], ascending=True).reset_index(drop=True)

    return df
