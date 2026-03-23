import hashlib
import json
import pandas as pd


def get_splits_signature(splits: list[list[str]]) -> str:
    # сортируем внутри каждого сплита и сами сплиты
    normalized = [sorted(split) for split in splits]
    normalized = sorted(normalized)

    s = json.dumps(normalized)
    return hashlib.md5(s.encode()).hexdigest()


def split_by_deployment(df: pd.DataFrame, n: int, signature: str = None) -> list[pd.DataFrame]:
    group_sizes = (df.groupby('deployment_id').size().reset_index(name='size')
                   .sort_values(['size', 'deployment_id'], ascending=[False, True], kind='mergesort'))
    splits: list[list[str]] = [[] for _ in range(n)]
    split_sizes = [0] * n

    for _, row in group_sizes.iterrows():
        idx = split_sizes.index(min(split_sizes))

        splits[idx].append(row['deployment_id'])
        split_sizes[idx] += row['size']

    if signature:
        current_signature = get_splits_signature(splits)
        assert current_signature == signature, f"Wrong signature: {current_signature} != {signature}"

    df_parts: list[pd.DataFrame] = []
    for split_groups in splits:
        df_parts.append(df[df['deployment_id'].isin(split_groups)])

    return df_parts
