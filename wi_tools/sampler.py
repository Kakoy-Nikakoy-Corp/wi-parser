import pandas as pd


def temperature_sampling(df, key, config):
    # Выравниваем распределение кадров внутри категории таким образом, чтобы уменьшить кол-во "крупных" видов
    # и сохранить при этом "мелкие" виды, повысив разнообразие в датасете
    sampled = []
    for category, options in config.items():
        target_amount = options[1]
        alpha = options[2]

        df_cat = df[df.category == category]
        counts = df_cat.groupby(key).size().reset_index(name='n')

        counts['weight'] = counts.n ** alpha
        counts.weight /= counts.weight.sum()
        counts['target'] = (counts.weight * target_amount).astype(int)

        for value, g in df_cat.groupby(key):
            n_target = counts.loc[counts[key] == value, 'target'].values[0]
            n = min(len(g), n_target)
            sampled.append(g.sample(n, random_state=42))

    return pd.concat(sampled).reset_index(drop=True)
