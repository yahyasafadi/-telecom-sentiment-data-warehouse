import sys, os, re
import pandas as pd
from datetime import datetime
from pathlib import Path

# Ajouter la racine du projet (Docker) au sys.path pour l'exécution
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

# Importer les modules NLP
from src.nlp.sentiment_analysis import get_sentiment_scores_batch
from src.nlp.topic_extraction import get_topic

def parse_relative_date(text: str) -> pd.Timestamp:
    text = str(text).lower()
    days = sum([
        int(re.search(r"(\d+)\s*an", text).group(1)) * 365 if re.search(r"(\d+)\s*an", text) else 0,
        int(re.search(r"(\d+)\s*mois", text).group(1)) * 30 if re.search(r"(\d+)\s*mois", text) else 0,
        int(re.search(r"(\d+)\s*semaine", text).group(1)) * 7 if re.search(r"(\d+)\s*semaine", text) else 0,
        int(re.search(r"(\d+)\s*jour", text).group(1)) if re.search(r"(\d+)\s*jour", text) else 0
    ])
    return pd.Timestamp(datetime.today()) - pd.Timedelta(days=days)

def clean_reviews():
    for op in ["IAM", "INWI", "Orange"]:
        input_path = f"data/raw/{op}/reviews.csv"
        if not os.path.exists(input_path): continue
        
        df = pd.read_csv(input_path)
        df.columns = df.columns.str.strip()
        
        # Filtrer et nettoyer les textes
        df["Comment"] = df["Comment"].astype(str).str.replace(r'[\n…]', ' ', regex=True).str.strip()
        df = df[df["Comment"].str.lower() != "aucun texte"].copy()
        
        # Gérer les dates
        df["review_date"] = df["Date"].apply(parse_relative_date)
        df["review_year"] = df["review_date"].dt.year
        df["review_month"] = df["review_date"].dt.month
        df["review_day"] = df["review_date"].dt.day
        
        # Appliquer NLP
        print(f"Analyse NLP pour {op} ({len(df)} avis)...")
        # Traitement ultra rapide en lot (batch) pour l'IA
        df["sentiment_score"] = get_sentiment_scores_batch(df["Comment"].tolist())
        df["topic"] = df["Comment"].apply(get_topic)
        df["comment_length"] = df["Comment"].str.len()
        
        # Sauvegarde
        cols = ["num_agence", "Name", "Comment", "review_year", "review_month", "review_day", "sentiment_score", "topic", "comment_length"]
        df[cols].to_csv(f"data/raw/{op}/cleaned_reviews.csv", index=False, encoding="utf-8")

if __name__ == "__main__":
    clean_reviews()
