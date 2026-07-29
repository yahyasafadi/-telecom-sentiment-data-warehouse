from sqlalchemy import create_engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv("C:/Users/moham/Desktop/Docker/.env")
engine = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")

with engine.connect() as conn: print("Connecté à la base !")

for dim in ['agence', 'temps', 'ville', 'topic', 'operateur', 'users', 'reviews']:
    pd.read_csv(f"C:/Users/moham/Desktop/Docker/data/dw_output/dim_{dim}.csv").to_sql(f"dim_{dim}", engine, if_exists="replace", index=False)

pd.read_csv("C:/Users/moham/Desktop/Docker/data/dw_output/fact_reviews.csv").to_sql("fact_table", engine, if_exists="replace", index=False)
