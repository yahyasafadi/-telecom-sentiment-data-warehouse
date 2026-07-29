# 📊 Analyse des Sentiments & Data Warehouse (Télécom Maroc)
Ce projet est une solution complète (End-to-End) de **Data Engineering** et de **Data Science** conçue pour analyser la satisfaction client des opérateurs télécoms au Maroc (IAM, INWI, Orange).
Il couvre l'intégralité du cycle de vie de la donnée : de l'extraction brute sur le web (Scraping) jusqu'à la modélisation en entrepôt de données (Data Warehouse) et la création de tableaux de bord Business Intelligence (BI).
## 🚀 Fonctionnalités Principales
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
## 🛠️ Stack Technique
- **Langage** : Python 3
- **Data Science / NLP** : `pandas`, `transformers` (HuggingFace)
- **Data Engineering** : `SQLAlchemy`, Architecture ETL (Extract, Transform, Load)
- **Infrastructure** : Docker, Docker Compose, PostgreSQL, pgAdmin
- **Visualisation** : Power BI (ou analyse locale via Jupyter Notebooks)
## 📂 Structure du Projet
```text
📁 Docker/
├── 📁 data/                  # Dossiers de stockage des données
│   ├── raw/                  # Fichiers bruts scrapés (CSV)
│   └── dw_output/            # Fichiers nettoyés et modélisés (Star Schema)
├── 📁 src/                   # Code source
│   ├── etl/                  # Scripts de transformation et modélisation (ETL)
