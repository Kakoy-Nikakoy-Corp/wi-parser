import pandas as pd


def temperature_sampling(df: pd.DataFrame, key: str, config: dict) -> pd.DataFrame:
    # Выравниваем распределение внутри категории таким образом, чтобы уменьшить кол-во "крупных" видов
    # и сохранить при этом "мелкие" виды, повысив разнообразие в датасете
    sampled: list[pd.DataFrame] = []
    for category, options in config.items():
        target_amount: int = options[1]  # Сколько хотим строк в итоговом датасете с данной категорией
        alpha: float = options[2]  # Температура внутри категории от 0 до 1

        df_cat = df[df.category == category]
        counts = df_cat.groupby(key).size().reset_index(name='n')  # Считаем начальное число особей каждого вида (n)

        counts['weight'] = counts.n ** alpha  # Вес = кол-во n с поправкой на температуру
        counts.weight /= counts.weight.sum()  # Нормируем вес, разделив его на сумму, чтобы получить вер-ть от 0 до 1
        counts['target'] = (counts.weight * target_amount).astype(int)  # Считаем целевое число особей

        # Сэмплируем виды
        for value, g in df_cat.groupby(key):
            n_target = counts.loc[counts[key] == value, 'target'].values[0]
            n = min(len(g), n_target)
            sampled.append(g.sample(n, random_state=42))

    return pd.concat(sampled).reset_index(drop=True)
