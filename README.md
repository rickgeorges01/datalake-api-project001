# API Data Lake 1

Ce projet est une API sécurisée et traçable permettant d'exposer des données issues d’un data lake simulé.
Il a été réalisé avec Django REST Framework, JWT pour la sécurité, SQLite pour le stockage local, et Streamlit pour l’interface de test interactive.

---

## Installation

### 1. Cloner le projet
```bash
git clone <url_du_repo>
cd data_lake_api
```

### 2. Créer et activer l'environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/macOS
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

---

## Lancer l’API Django

```bash
python manage.py migrate
python manage.py createsuperuser  # si nécessaire
python manage.py runserver
```

---

## Accès à l'API

| Composant              | URL                                    |
|------------------------|-----------------------------------------|
| Swagger (doc auto)     | http://127.0.0.1:8000/swagger/          |
| Interface Streamlit    | http://localhost:8501                   |
| Admin Django           | http://127.0.0.1:8000/admin/            |

---

## Lancer l’interface Streamlit

```bash
streamlit run app.py
```

Fonctionnalités de l’app :
- 🔐 Connexion via JWT
- 📂 Aperçu et export du dataset
- 📄 Requêtes paramétrables (filtres, projections)
- 📊 Métriques analytiques
- 🔍 Recherche full-text
- 🧾 Audit et lineage
- 🔁 Simulation repush Kafka
- 🧠 Déclenchement d'un modèle ML simulé

---

## Importer les données (dataset CSV enrichi)

```bash
python manage.py import_transactions
```

Le fichier utilisé se trouve dans `bronze/global_superstore_enriched.csv`

---

## Authentification (JWT)

- Endpoint : `/api/token/`
- Utiliser le token pour accéder aux routes sécurisées
- Streamlit gère cette connexion automatiquement

---

## Endpoints disponibles (résumé)

- `GET /api/transactions/`
- `GET /api/metrics/<nom_metric>/`
- `GET /api/search/?q=...`
- `GET /api/audit/`
- `GET /api/lineage/<id>/`
- `POST /api/repush/<id>/`
- `POST /api/train-ml/`

---

## Fonctionnalités avancées

- 🔍 **Search** : recherche multi-champs
- 📊 **Métriques** : dépense moyenne, top produits, CA par pays, etc.
- 🧾 **Audit & Lineage** : suivi des accès et journalisation
- 🧠 **ML Simulation** : fonction de machine learning simulée

---

## À propos

Projet réalisé par **Rick Georges YELEUMEU**   


---

## Structure du dépôt

```bash
projet_datalake_api/
├── data_lake_api/          # Projet Django complet
├── app.py                  # Application Streamlit de test
├── requirements.txt        # Dépendances
├── architecture.png        # Diagramme d’architecture
├── README.md               # Ce fichier
```

---

## Remarques

- L’ensemble fonctionne en local sans besoin de déploiement cloud
- Peut être porté facilement vers PostgreSQL + Docker pour industrialisation
- Toutes les fonctions sont testables via Swagger ou Streamlit

Bonne exploration
