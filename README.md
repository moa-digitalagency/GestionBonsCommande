# SaaS BTP Commande

Application SaaS multi-tenant pour la gestion de Bons de Commande de matériaux/matériels BTP au Maroc.

## Fonctionnalités
- **Multi-tenant** : Isolation stricte des données par société.
- **Workflow** : Cycle de vie complet (Brouillon -> Soumis -> Validé -> PDF -> Partagé).
- **Traduction & Dictionnaire** : Support multilingue (Français, Arabe, Darija, Anglais, Espagnol) avec dictionnaire enrichissable.
- **PDF** : Génération de Bons de Commande PDF avec branding société.

## Installation

1.  **Prérequis**
    - Python 3.8 ou supérieur.
    - pip (gestionnaire de paquets Python).

2.  **Installation des dépendances**
    ```bash
    pip install -r requirements.txt
    ```
    *Note : Pour la génération PDF, WeasyPrint peut nécessiter des bibliothèques systèmes supplémentaires (cairo, pango).*

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
