# Migration CSV -> MongoDB

## Objectif
Fournir un script réutilisable pour migrer les données d'un fichier CSV vers une base de données MongoDB en :
- vérifiant l'intégrité des données avant et après migration,
- appliquant un typage simple,
- supprimant les doublons,
- automatisant des tests, et
- créant des index pertinents.

## Utilisation avec uv (recommandé)
Ce projet utilise uv pour gérer les dépendances et l'environnement virtuel.

## Prérequis
- Installer MongoDB localement (ex : via les paquets officiels ou docker).
- Python 3.10+ recommandé.
- Créer un environnement virtuel.

## Installation (exemple)
```bash
# dans le dossier project/
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt