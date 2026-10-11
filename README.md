<<<<<<< HEAD
# 📊 Analyse des Sentiments & Data Warehouse
Ce projet est une solution complète (End-to-End) de **Data Engineering** et de **Data Science** conçue pour analyser la satisfaction client des opérateurs télécoms au Maroc (IAM, INWI, Orange).
Il couvre l'intégralité du cycle de vie de la donnée : de l'extraction brute sur le web (Scraping) jusqu'à la modélisation en entrepôt de données (Data Warehouse) et la création de tableaux de bord Business Intelligence (BI).
## 🚀 Fonctionnalités Principales
=======
# 📊 Analyse des Sentiments & Data Warehouse (Télécom Maroc)

Ce projet est une solution complète (End-to-End) de **Data Engineering** et de **Data Science** conçue pour analyser la satisfaction client des opérateurs télécoms au Maroc (IAM, INWI, Orange).

Il couvre l'intégralité du cycle de vie de la donnée : de l'extraction brute sur le web (Scraping) jusqu'à la modélisation en entrepôt de données (Data Warehouse) et la création de tableaux de bord Business Intelligence (BI).

## 🚀 Fonctionnalités Principales

>>>>>>> cd7283c (new changes)
1. **Data Extraction (Scraping)** : Récupération automatisée des avis clients et des informations des agences depuis diverses sources.
2. **Traitement NLP (Intelligence Artificielle)** :
   - Analyse des sentiments (Score de -1 à 1) via des modèles **HuggingFace** (`pipeline`).
   - Classification "Zero-Shot" pour catégoriser automatiquement les sujets abordés par les clients (ex: Réseau, Facturation, Service Client).
   - Optimisation par traitement en lots (Batch processing) pour garantir des performances élevées.
3. **Data Engineering & Modélisation** :
   - Nettoyage et transformation des données brutes avec `pandas`.
   - Modélisation de la base de données en **Schéma en Étoile** (Star Schema) avec une table de faits (`fact_reviews`) et plusieurs dimensions (`dim_operateur`, `dim_temps`, `dim_ville`, `dim_topic`, etc.).
4. **Data Storage & DevOps** :
   - Déploiement d'une base de données **PostgreSQL** conteneurisée avec **Docker** (`docker-compose`).
   - Chargement automatisé (Load) des données depuis Python vers la base de données via `SQLAlchemy`.
5. **Business Intelligence (BI)** :
   - Création de Vues SQL (Views) optimisées dans PostgreSQL.
   - Intégration et Visualisation directes avec **Power BI** (DirectQuery/Import).
<<<<<<< HEAD
## 🛠️ Stack Technique
=======

## 🛠️ Stack Technique

>>>>>>> cd7283c (new changes)
- **Langage** : Python 3
- **Data Science / NLP** : `pandas`, `transformers` (HuggingFace)
- **Data Engineering** : `SQLAlchemy`, Architecture ETL (Extract, Transform, Load)
- **Infrastructure** : Docker, Docker Compose, PostgreSQL, pgAdmin
- **Visualisation** : Power BI (ou analyse locale via Jupyter Notebooks)
<<<<<<< HEAD
## 📂 Structure du Projet
=======

## 📂 Structure du Projet

>>>>>>> cd7283c (new changes)
```text
📁 Docker/
├── 📁 data/                  # Dossiers de stockage des données
│   ├── raw/                  # Fichiers bruts scrapés (CSV)
│   └── dw_output/            # Fichiers nettoyés et modélisés (Star Schema)
├── 📁 src/                   # Code source
│   ├── etl/                  # Scripts de transformation et modélisation (ETL)
<<<<<<< HEAD
=======
│   ├── nlp/                  # Modules d'Intelligence Artificielle (HuggingFace)
│   └── scrapers/             # Scripts de collecte de données
├── 📁 postgres/              # Fichiers d'initialisation de la DB
├── .env                      # Variables d'environnement (Identifiants DB)
├── docker-compose.yml        # Configuration de l'infrastructure Docker
└── README.md                 # Documentation du projet
```

## ⚙️ Comment exécuter le projet

### 1. Prérequis
- Python 3.10+
- Docker & Docker Desktop installés
- Un environnement virtuel Python (`venv`) activé avec les dépendances installées (`pip install -r requirements.txt`).

### 2. Démarrer l'infrastructure de la Base de Données
Assurez-vous que votre fichier `.env` contient les bonnes variables d'environnement (ex: `POSTGRES_USER=root`, `POSTGRES_PASSWORD=root`), puis lancez :
```bash
docker-compose up -d
```
Cela démarrera PostgreSQL sur le port `5432` et pgAdmin sur le port `5050`.

### 3. Exécuter le Pipeline de Données (ETL)
Exécutez les scripts Python dans cet ordre pour traiter les données de bout en bout :

```bash
# 1. Nettoyer les données brutes et appliquer les modèles NLP
python src/etl/clean_agencies.py
python src/etl/clean_reviews.py

# 2. Modéliser les données en Schéma en Étoile (Star Schema)
python src/etl/build_data_warehouse.py

# 3. Charger le Data Warehouse dans PostgreSQL
python src/etl/load_to_database.py
```

### 4. Visualisation (Power BI)
- Ouvrez Power BI Desktop.
- Connectez-vous à la base de données PostgreSQL (`localhost:5432`).
- Importez les vues créées (ou les tables directes) pour générer votre tableau de bord interactif comparant la satisfaction des opérateurs télécoms.

---
*Projet réalisé dans un cadre académique pour démontrer des compétences en Ingénierie des données et en Data Science.*
>>>>>>> cd7283c (new changes)
