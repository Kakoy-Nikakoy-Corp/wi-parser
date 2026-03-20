import os
import pandas as pd
from dotenv import load_dotenv

from wi_tools import split_by_deployment, download_images, organize_images, load_dataset, temperature_sampling

load_dotenv()

part_num = int(os.getenv("PART"))
signature = os.getenv("SIGNATURE")
email = os.getenv("WI_EMAIL")
password = os.getenv("WI_PASSWORD")

# Similar mammals
A = ['Leopard Cat', 'Eurasian Lynx', 'Blue Sheep', 'Takin', 'Grey Wolf', 'Chinese Goral', 'Red Fox', 'Forest Musk Deer',
     'Tibetan Fox', 'Dhole', 'Asiatic Wild Ass', 'Alpine Musk Deer', 'Argali', 'Chinese Serow', 'Siberian Ibex']

# Other mammals
B = ['Chinese Red Pika', 'Rabbit and Hare Family', 'Mammal', 'Carnivorous Mammal', 'Domestic Dog',
     'Himalayan Marmot', 'Hylobatidae Family', 'Beech Marten', 'Moupin Pika', 'Yellow-throated Marten',
     'Greater Hog Badger', 'Siberian Weasel', 'Ochotona Species', 'Altai Weasel', 'Marmota Species', 'Woolly Hare',
     'Rodent', 'Bactrian Camel', 'Tolai Hare', 'Red Panda', 'Sambar', 'Asiatic Black Bear', 'Wild Boar', 'Brown Bear',
     'Goitered Gazelle']

# Birds
C = ['Tibetan Snowcock', 'Chestnut-throated Partridge', 'Chinese Monal', 'Bird', 'Blood Pheasant', 'Snow Partridge',
     "Przevalski's Partridge", 'Red-billed Chough', "Temminck's Tragopan", 'Golden Eagle', 'Himalayan Griffon',
     'Yellow-billed Chough']

# Empty images
D = ['Blank', 'Misfire']

CAT_CONFIG = {
    'A': [A, 2500, 0.3],
    'B': [B, 1500, 0.4],
    'C': [C, 500, 0.5],
    'D': [D, 1000, 1],
}

# ищем все image_id/deployments_id, где есть барсы
positives = load_dataset('./dataset/positive-samples')
leopard_images = positives['image_id'].unique()
leopard_deployments = positives['deployment_id'].unique()

df = load_dataset('./dataset/negative-samples')

# оставляем в images только кадры без барсов и только с тех камер, где барсы ранее были замечены
# + убираем "неудачные" фото, где common_name = Animal (животное подошло очень близко и невозможно
# идентифицировать вид)
df = df[
    (~df.image_id.isin(leopard_images)) & df.deployment_id.isin(leopard_deployments)
    & (df.common_name != 'Animal')
]

df['category'] = pd.Series(dtype='str')

for cat, options in CAT_CONFIG.items():
    df.loc[df.common_name.isin(options[0]), 'category'] = cat

df = temperature_sampling(df, 'common_name', CAT_CONFIG)
part = split_by_deployment(df, 5, signature)[part_num]

download_images(part, 'negative', email, password)
organize_images(part, 'negative')
