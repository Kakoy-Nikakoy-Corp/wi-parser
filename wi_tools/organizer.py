import pandas as pd
import shutil
from pathlib import Path
from tqdm import tqdm


def organize_images(df, label):
    output_path = Path('./output') / label
    downloads_path = Path('./download') / label

    # Sort the entire dataframe by deployment_id and then timestamp
    df_sorted = df.sort_values(by=["deployment_id", "timestamp"], ascending=True).reset_index(drop=True)

    # Track current number for each deployment
    deployment_counters = {}

    # Process rows — copy with sequential numbering per deployment
    kept_rows = []
    for _, row in tqdm(df_sorted.iterrows(), total=len(df_sorted), desc="Organizing images"):
        source_path = downloads_path / f"{row['image_id']}.jpg"

        if not source_path.is_file():
            continue
        kept_rows.append(row)

        deployment = row["deployment_id"]

        # Destination folder: output/<label>/<deployment_id>/
        dest_dir = output_path / deployment
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Get next number for this deployment
        if deployment not in deployment_counters:
            deployment_counters[deployment] = 1
        else:
            deployment_counters[deployment] += 1

        next_num = deployment_counters[deployment]

        new_filename = f"{next_num:04d}_{row['timestamp']}.jpg"
        dest_path = dest_dir / new_filename

        shutil.copy2(source_path, dest_path)

    pd.DataFrame(kept_rows).to_csv(output_path / "kept_images.csv", index=False)
