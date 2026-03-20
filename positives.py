import os
from dotenv import load_dotenv

from wi_tools import load_dataset, download_images, organize_images

load_dotenv()
email = os.getenv("WI_EMAIL")
password = os.getenv("WI_PASSWORD")

df = load_dataset('./dataset/positive-samples')

download_images(df, 'positive', email, password)
organize_images(df, 'positive')
