![Python Version](https://img.shields.io/badge/Python-3.12-blue?style=flat-square) ![Framework](https://img.shields.io/badge/Framework-Flask-green?style=flat-square) ![Database](https://img.shields.io/badge/Database-SQLAlchemy-orange?style=flat-square) ![Status](https://img.shields.io/badge/Status-Private%2FInternal-red?style=flat-square) ![License](https://img.shields.io/badge/License-Proprietary-black?style=flat-square) ![Owner](https://img.shields.io/badge/Owner-MOA_Digital_Agency-purple?style=flat-square)

[ 🇫🇷 **Français** ](README.md) | [ 🇬🇧 English ](README_en.md)

# BTP Commande - Plateforme de Gestion des Achats

> **AVERTISSEMENT JURIDIQUE :** Ce logiciel est la propriété exclusive de **MOA Digital Agency**. Toute reproduction, distribution ou utilisation non autorisée est strictement interdite. Code source confidentiel.

## 📌 Présentation

**BTP Commande** est une solution SaaS propriétaire conçue pour optimiser et sécuriser le processus d'achat dans le secteur du Bâtiment et des Travaux Publics. Elle permet la gestion complète du cycle de vie des commandes, de la création du brouillon à la génération de bons de commande officiels en PDF, avec un fort accent sur la traduction technique (Français / Arabe / Darija) pour faciliter les échanges avec les fournisseurs.

## 🏗️ Architecture Technique

```mermaid
graph TD
    User([Utilisateur]) -->|HTTPS| Nginx[Nginx Reverse Proxy]
    Nginx -->|Proxy Pass| Gunicorn[Gunicorn App Server]
    Gunicorn -->|WSGI| FlaskApp[Application Flask]

    subgraph "Coeur BTP Commande"
        FlaskApp --> Auth["Auth (Login/RBAC)"]
        FlaskApp --> Orders["Commandes (CRUD)"]
        FlaskApp --> Lexique["Dictionnaire (Traduction)"]

        Auth --> DB[("PostgreSQL/SQLite")]
        Orders --> DB
        Lexique --> DB

        Orders --> PDF["Service PDF (WeasyPrint)"]
        PDF --> Storage["Stockage Local (Static)"]
    end

    subgraph "Client / Assets"
        Browser[Navigateur Client] -->|Charge| Tailwind[Tailwind CSS (CDN)]
        Browser -->|Charge| Alpine[Alpine.js (CDN)]
        Browser -->|Charge| Fonts["Google Fonts (Inter/Cairo)"]
    end
```

## 📚 Documentation

Toute la documentation technique et fonctionnelle est disponible dans le dossier `docs/`.

| Document | Description | Public |
| :--- | :--- | :--- |
| [**La Bible des Fonctionnalités**](docs/BTP_Commande_features_full_list.md) | Liste exhaustive de toutes les règles métier et micro-fonctionnalités. | Product Owners / Devs |
| [**Architecture Technique**](docs/BTP_Commande_technical_architecture.md) | Détails sur la stack, la base de données et les flux. | Développeurs / DevOps |
| [**Guide de Déploiement**](docs/BTP_Commande_deployment_guide.md) | Procédures d'installation (Local & VPS). | DevOps / SysAdmin |
| [**Manuel Utilisateur**](docs/BTP_Commande_user_guide.md) | Guide d'utilisation pour les chefs de chantier et acheteurs. | Utilisateurs Finaux |

## ✨ Fonctionnalités Clés

*   **Workflow de Validation Strict :** Brouillon -> Soumis -> Validé -> PDF généré.
*   **Moteur PDF WeasyPrint :** Génération de documents haute fidélité avec protection LFI.
*   **Dictionnaire Intelligent :** Traduction automatique des termes techniques BTP.
*   **Multi-Tenant :** Isolation totale des données par entreprise.
*   **Interface Réactive :** Utilisation d'Alpine.js pour une expérience fluide sans lourdeur SPA.

## 🚀 Installation Rapide (Dev)

Voir le [Guide de Déploiement](docs/BTP_Commande_deployment_guide.md) pour les détails complets.

```bash
# 1. Cloner le dépôt (Accès restreint)
git clone <url-interne>

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Initialiser la BDD
python init_db.py

# 4. Lancer le serveur
flask run
```

---
&copy; 2024 MOA Digital Agency. Tous droits réservés. Auteur : Aisance KALONJI.
