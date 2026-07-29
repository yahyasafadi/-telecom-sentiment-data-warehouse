from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis", model="lxyuan/distilbert-base-multilingual-cased-sentiments-student")

def get_sentiment_scores_batch(texts: list) -> list:
    """
    Traite une liste complète de textes d'un coup (Batching).
    C'est la méthode ultime pour avoir la précision d'un modèle IA profond SANS que ce soit lent !
    """
    if not texts:
        return []
    
    # Sécurisation des textes
    clean_texts = [str(t)[:512] for t in texts]
    
    try:
        results = sentiment_pipeline(clean_texts, batch_size=32)
        
        scores = []
        for res in results:
            if res['label'] == 'positive':
                scores.append(round(res['score'], 2))
            elif res['label'] == 'negative':
                scores.append(round(-res['score'], 2))
            else:
                scores.append(0.0)
                
        return scores
        
    except Exception as e:
        print(f"Erreur IA : {e}")
        return [0.0] * len(texts)