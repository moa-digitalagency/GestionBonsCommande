# SaaS BTP Commande

Application SaaS multi-tenant pour la gestion de Bons de Commande de matériaux/matériels BTP au Maroc.

## Fonctionnalités
- **Multi-tenant** : Isolation stricte des données par société.
- **Workflow** : Cycle de vie complet (Brouillon -> Soumis -> Validé -> PDF -> Partagé).
- **Traduction & Dictionnaire** : Support multilingue (Français, Arabe, Darija, Anglais, Espagnol) avec dictionnaire enrichissable.
- **PDF** : Génération de Bons de Commande PDF avec branding société.

## Installation

### 1. Prérequis
- Python 3.8 ou supérieur.
- pip (gestionnaire de paquets Python).

### 2. Installation sur un serveur VPS (Debian/Ubuntu)

La génération de PDF utilise la bibliothèque WeasyPrint, qui nécessite des dépendances système spécifiques (Pango, Cairo, etc.) qui ne sont pas installées par défaut.

Si vous rencontrez l'erreur `OSError: cannot load library 'pango-1.0-0'`, suivez ces étapes :

**Option A : Utiliser le script d'installation automatique**
```bash
# Rendre le script exécutable
chmod +x setup_vps.sh

# Exécuter avec les droits root (sudo)
sudo ./setup_vps.sh
```

**Option B : Installation manuelle des dépendances**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 libjpeg-dev libopenjp2-7-dev libffi-dev shared-mime-info
pip install -r requirements.txt
```

### 3. Installation standard (Local/Dev)
```bash
pip install -r requirements.txt
```

### 4. Déploiement via Docker
Un `Dockerfile` est fourni pour faciliter le déploiement conteneurisé.

```bash
# Construire l'image
docker build -t btp-commande .

# Lancer le conteneur
docker run -p 5000:5000 btp-commande
```

## Configuration Base de Données

L'application est configurée pour utiliser SQLite par défaut, ou PostgreSQL via `DATABASE_URL`.

1.  **Initialisation**
    Exécutez le script d'initialisation pour créer les tables et les données de base :
    ```bash
    python init_db.py
    ```
    Cela va :
    - Créer la structure de la base de données.
    - Peupler le dictionnaire BTP avec une liste de termes courants.
    - Créer un utilisateur Super Admin par défaut :
      - Email : `admin@btpcommande.ma`
      - Mot de passe : `admin123`

## Lancement

Pour démarrer le serveur de développement :

```bash
python app.py
```
L'application sera accessible sur `http://localhost:5000`.

## Tests

Le projet inclut une suite de tests couvrant l'authentification, l'isolation multi-tenant, le workflow de commande et le dictionnaire.

Pour lancer les tests :

```bash
pytest
```

## Structure du Projet
- `app.py`: Point d'entrée de l'application.
- `models/`: Définition des modèles de données (SQLAlchemy).
- `routes/`: Définition des routes et contrôleurs (Flask Blueprints).
- `services/`: Couche de service contenant la logique métier.
- `templates/`: Templates HTML (Jinja2).
- `tests/`: Tests unitaires et d'intégration.
