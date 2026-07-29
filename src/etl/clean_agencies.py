import pandas as pd
import os

def clean_agencies():
    for op in ["IAM", "INWI", "Orange"]:
        input_path = f"data/raw/{op}/data_agences.csv"
        if not os.path.exists(input_path): continue
        
        df = pd.read_csv(input_path)
        # Nettoyage ultra simple
        df['adresse'] = df['adresse'].astype(str).str.replace(r'[\n\r]', '', regex=True).str.strip()
        df["num_agence"] = df["num_agence"].astype(float).astype(int, errors='ignore')
        
        df.drop_duplicates().to_csv(f"data/raw/{op}/data_agences_cleaned.csv", index=False)
        print(f"Agences nettoyées pour {op}")

if __name__ == "__main__":
    clean_agencies()
