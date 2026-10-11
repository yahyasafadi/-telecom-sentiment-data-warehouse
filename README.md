# 📊 Analyse des Sentiments & Data Warehouse (Télécom Maroc)

Solution complète (**End-to-End**) de **Data Engineering**, **NLP (Intelligence Artificielle)** et **Business Intelligence**, conçue pour collecter, modéliser et analyser la satisfaction des clients des trois opérateurs télécoms majeurs au Maroc : **IAM (Maroc Telecom)**, **Orange Maroc** et **inwi**.

Le pipeline couvre l'intégralité du cycle de vie de la donnée : du web scraping Google Maps à la restitution interactive via **Streamlit** et **Power BI**, en passant par un entrepôt de données modélisé en **schéma en étoile (*Star Schema*)** sous **PostgreSQL**.

---

## 📑 Sommaire
- [Architecture & Flux de Données](#-architecture--flux-de-données)
- [Modélisation Décisionnelle (Schéma en Étoile)](#-modélisation-décisionnelle-schéma-en-étoile)
- [Dashboard Interactif Streamlit](#-dashboard-interactif-streamlit)
- [Arborescence du Projet](#-arborescence-du-projet)
- [Installation & Démarrage Rapide](#-installation--démarrage-rapide)
- [Stack Technique](#-stack-technique)

---

## 🔄 Architecture & Flux de Données

```
[Google Maps] 
      │ (Web Scraping Selenium / undetected-chromedriver)
      ▼
[Données Brutes (data/raw)]
      │
      ├─► [Nettoyage & Prétraitement (pandas)]
      ├─► [NLP HuggingFace : Sentiment (-1 à +1)]
      └─► [NLP Classification Zero-Shot : Topics]
      │
      ▼
[Data Warehouse Output (data/dw_output)]
      │ (Star Schema : fact_reviews + dimensions)
      │
      ├─► [PostgreSQL via Docker Compose & SQLAlchemy] ──► [Power BI]
      │
      └─► [Dashboard Interactif Streamlit & Plotly (app.py)]
```

---

## 🌟 Modélisation Décisionnelle (Schéma en Étoile)

Les données nettoyées et enrichies par l'IA sont structurées en un **Star Schema** optimal pour l'analyse décisionnelle (OLAP) :

### Table de Faits : `fact_reviews`
* **Granularité** : Un avis client unique (`review_id`).
* **Clés étrangères (FK)** : `agence_id`, `temps_id`, `user_id`, `topic_id`, `ville_id`, `operateur_id`.
* **Mesures quantitatives** :
  * `sentiment_score` : Score continu de sentiment calculé par NLP (entre `-1.0` et `+1.0`).
  * `comment_length` : Longueur du commentaire (en nombre de caractères).

### Tables de Dimensions
1. **`dim_operateur`** : `operateur_id`, `operateur_name` (*IAM*, *Orange*, *INWI*).
2. **`dim_agence`** : `agence_id`, `num_agence`, `nom_agence`, `adresse`.
3. **`dim_ville`** : `ville_id`, `ville` (*Casablanca, Rabat, Marrakech, Tanger, Fès, etc.*).
4. **`dim_temps`** : `temps_id`, `review_year`, `review_month`, `review_day`.
5. **`dim_topic`** : `topic_id`, `topic` (*attente en agence, carte sim et réseau, fibre optique, facturation, service client...*).
6. **`dim_users`** : `user_id`, `Name` (auteur de l'avis).
7. **`dim_reviews`** : `review_id`, `Comment`, `sentiment_score` (texte intégral brut).

---

## 📈 Dashboard Interactif Streamlit (`app.py`)

L'application Streamlit propose 5 modules analytiques principaux :

1. **Comparaison Globale des Sentiments** : Diagramme en barres comparant les scores moyens et les taux de satisfaction d'IAM, Orange et inwi.
2. **Analyse du Sentiment par Ville** : Classement horizontal des villes marocaines avec sélecteur d'opérateur dynamique.
3. **Répartition Globale des Topics** : Diagramme en anneau (*Donut Chart*) détaillant les thématiques dominantes de l'ensemble des clients.
4. **Répartition des Topics par Opérateur** : Filtre interactif par opérateur pour identifier ses points forts et points de friction spécifiques.
5. **Évolution Temporelle du Sentiment** : Analyse des tendances au fil du temps (par mois ou par année) avec mode multi-opérateurs.
6. **Explorateur d'Avis (Drill-Down)** : Moteur de recherche et consultation des commentaires réels avec filtres avancés.

---

## 📁 Arborescence du Projet

```text
Docker/
├── data/
│   ├── raw/                       # Données brutes scrapées par opérateur (IAM, INWI, Orange)
│   └── dw_output/                 # Tables du Data Warehouse modélisées (CSV)
│       ├── fact_reviews.csv
│       ├── dim_operateur.csv
│       ├── dim_agence.csv
│       ├── dim_ville.csv
│       ├── dim_temps.csv
│       ├── dim_topic.csv
│       ├── dim_users.csv
│       └── dim_reviews.csv
├── src/
│   ├── etl/                       # Pipeline ETL
│   │   ├── clean_agencies.py      # Nettoyage des agences
│   │   ├── clean_reviews.py       # Prétraitement et enrichissement IA
│   │   ├── build_data_warehouse.py# Génération du Schéma en Étoile
│   │   └── load_to_database.py    # Chargement dans PostgreSQL
│   ├── nlp/                       # Modèles d'Intelligence Artificielle
│   │   ├── sentiment_analysis.py  # Pipeline HuggingFace (DistilBERT)
│   │   └── topic_extraction.py    # Classification thématique Zero-Shot
│   └── scrapers/                  # Collecte web automatisée
│       ├── extract_agencies.py    # Scraping des agences sur Google Maps
│       └── extract_reviews.py     # Scraping des avis clients
├── app.py                         # Application Dashboard interactive Streamlit
├── requirements.txt               # Dépendances Python du projet
├── docker-compose.yml             # Services Docker (PostgreSQL & pgAdmin)
├── .env                           # Configuration et identifiants de la base de données
└── README.md                      # Documentation du projet
```

---

## ⚙️ Installation & Démarrage Rapide

### 1. Prérequis
- **Python 3.10+**
- **Docker & Docker Desktop** installés (pour la base PostgreSQL)
- Google Chrome (si vous souhaitez réexécuter les scrapers)

### 2. Configuration de l'environnement Python
Clonez le dépôt, créez un environnement virtuel et installez les dépendances :
```bash
python -m venv venv
.\venv\Scripts\activate    # Sur Windows (ou source venv/bin/activate sur Linux/Mac)
pip install -r requirements.txt
```

### 3. Démarrer la Base de Données (PostgreSQL)
Démarrez les conteneurs PostgreSQL et pgAdmin en arrière-plan :
```bash
docker-compose up -d
```
* **PostgreSQL** est accessible sur `localhost:5432`.
* **pgAdmin** est accessible sur `http://localhost:5050`.

### 4. Exécuter le Pipeline ETL (si recalcul nécessaire)
Si vous souhaitez retraiter les données de zéro :
```bash
# Nettoyage et enrichissement IA (NLP)
python src/etl/clean_agencies.py
python src/etl/clean_reviews.py

# Modélisation en schéma en étoile
python src/etl/build_data_warehouse.py

# Chargement dans la base de données PostgreSQL
python src/etl/load_to_database.py
```

### 5. Lancer le Dashboard Streamlit
Lancez l'interface web interactive :
```bash
streamlit run app.py
```
L'application s'ouvre automatiquement dans votre navigateur à l'adresse : **`http://localhost:8501`**.

---

## 🛠️ Stack Technique

- **Langage & Traitement** : Python, Pandas, NumPy
- **Intelligence Artificielle (NLP)** : Hugging Face Transformers (`distilbert-base-multilingual-cased-sentiments-student`), Regex / NFD Normalization
- **Web Scraping** : Selenium, `undetected-chromedriver`, BeautifulSoup4
- **Base de Données & Data Warehouse** : PostgreSQL 15, SQLAlchemy, Docker Compose
- **Visualisation & BI** : Streamlit, Plotly Express & Graph Objects, Power BI Desktop
