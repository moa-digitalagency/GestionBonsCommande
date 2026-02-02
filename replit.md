# BTP Commande - Application SaaS de Gestion de Bons de Commande BTP (Maroc)

## Overview
Application SaaS multi-tenant pour la gestion des bons de commande de matériaux et matériels dans le secteur BTP au Maroc. Elle offre un support multilingue (Français, Arabe, Darija, Anglais, Espagnol) avec un dictionnaire BTP intelligent.

## Architecture

### Stack Technologique
- **Backend**: Python 3.11+ avec Flask
- **Base de données**: PostgreSQL avec SQLAlchemy ORM
- **Frontend**: HTML5, Tailwind CSS, Alpine.js
- **Génération PDF**: WeasyPrint

### Structure des dossiers
```
/
├── algorithms/          # Algorithmes métier
├── config/              # Configuration (settings.py)
├── docs/                # Documentation
├── lang/                # Fichiers de traduction
├── models/              # Modèles SQLAlchemy
│   ├── company.py       # Sociétés (tenants)
│   ├── user.py          # Utilisateurs
│   ├── project.py       # Chantiers
│   ├── product.py       # Articles catalogue
│   ├── order.py         # Bons de commande et lignes
│   └── lexique.py       # Dictionnaire BTP
├── routes/              # Routes Flask (blueprints)
├── scripts/             # Scripts utilitaires
├── security/            # Décorateurs sécurité
├── services/            # Services métier
│   ├── tenant_service   # Isolation multi-tenant
│   ├── order_service    # Workflow BC
│   ├── lexique_service  # Dictionnaire
│   └── pdf_service      # Génération PDF
├── statics/             # Fichiers statiques
│   ├── css/
│   ├── js/
│   ├── img/
│   └── uploads/
├── templates/           # Templates Jinja2
├── utils/               # Utilitaires
├── app.py               # Application Flask
├── init_db.py           # Initialisation BDD
└── requirements.txt     # Dépendances Python
```

## Rôles utilisateurs
1. **Super-Admin**: Gestion globale, dictionnaire BTP, sociétés
2. **Admin Société**: Paramètres société, utilisateurs, chantiers, articles
3. **Valideur**: Validation des BC, génération PDF
4. **Demandeur**: Création de BC, suggestions dictionnaire

## Workflow Bon de Commande
BROUILLON → SOUMIS → VALIDÉ → PDF_GÉNÉRÉ → PARTAGÉ

## Identifiants de test
- Super Admin: admin@btpcommande.ma / admin123

## Configuration requise
- DATABASE_URL (PostgreSQL)
- SESSION_SECRET

## Commandes
- Initialiser BDD: `python init_db.py`
- Lancer serveur: `python app.py`

## Recent Changes
- 2024: Création initiale de l'application MVP
- Implémentation complète du workflow BC
- Dictionnaire BTP avec 50 termes initiaux
- Interface mobile-first responsive
