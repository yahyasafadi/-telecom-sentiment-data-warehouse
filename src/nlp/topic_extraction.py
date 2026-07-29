import re
import unicodedata

TOPICS = {
    "carte sim et réseau": ["sim", "puce", "recharge", "forfait", "4g", "5g", "connexion", "reseau", "debit", "coupure", "signal"],
    "internet fibre et box": ["fibre", "box", "adsl", "routeur", "wifi", "installation", "technicien", "cablage"],
    "attente en agence et personnel": ["agence", "attente", "queue", "personnel", "vendeur", "accueil", "impoli", "comportement", "service"],
    "service client et assistance": ["service client", "appel", "repondre", "telephone", "reclamation", "support", "conseiller"],
    "facturation et prix": ["facture", "arnaque", "vol", "argent", "remboursement", "payer", "prix", "cher", "abonnement"],
    "application mobile et espace client": ["application", "app", "site", "bug", "mise a jour", "compte", "mot de passe"],
}

def clean_text_for_search(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(text).lower()) if unicodedata.category(c) != "Mn")

def get_topic(comment: str) -> str:
    """
    Assigne le sujet avec une méthode ultra-rapide par recherche de mots-clés.
    """
    if not isinstance(comment, str) or len(comment) < 5: 
        return "autre"
        
    norm_comment = clean_text_for_search(comment)
    
    # Compte les occurrences de mots-clés pour chaque sujet de façon hyper rapide
    scores = {}
    for topic, keywords in TOPICS.items():
        pattern = r"\b(" + "|".join(keywords) + r")\b"
        matches = re.findall(pattern, norm_comment)
        scores[topic] = len(matches)
        
    best_topic = max(scores, key=scores.get)
    
    if scores[best_topic] > 0:
        return best_topic
    return "autre"