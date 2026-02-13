# BTP Commande - Plateforme de Gestion des Achats BTP

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![Framework](https://img.shields.io/badge/flask-3.0-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![License](https://img.shields.io/badge/license-proprietary-red.svg)

**BTP Commande** est une solution SaaS complète conçue pour digitaliser et simplifier le processus d'achat dans le secteur du Bâtiment et Travaux Publics. Elle comble le fossé linguistique et technique entre les chantiers et les fournisseurs grâce à un moteur de traduction intelligent et une gestion rigoureuse des bons de commande.

---

## 📚 Documentation Complète

La documentation détaillée se trouve dans le dossier `docs/` :

| Document | Description | Cible |
| :--- | :--- | :--- |
| [**Fonctionnalités (Bible)**](docs/BTP_Commande_features_full_list.md) | Liste exhaustive de toutes les features et règles métier. | Tout le monde |
| [**Architecture Technique**](docs/BTP_Commande_technical_architecture.md) | Structure du code, Schéma BDD, Stack, Sécurité. | Développeurs |
| [**Guide de Déploiement**](docs/BTP_Commande_deployment_guide.md) | Installation locale, VPS, Docker, Variables d'env. | DevOps / SysAdmin |
| [**Manuel Utilisateur**](docs/BTP_Commande_user_guide.md) | Guide pas-à-pas pour créer des commandes et valider. | Utilisateurs finaux |

---

## ✨ Fonctionnalités Clés

*   **Workflow de Commande Strict :** Cycle de vie maîtrisé (Brouillon &rarr; Soumis &rarr; Validé &rarr; PDF).
*   **Moteur de Traduction BTP :** Traduction automatique des articles (Français &leftrightarrow; Arabe/Darija) pour les fournisseurs.
*   **Génération PDF Sécurisée :** Création de bons de commande officiels via `WeasyPrint` avec protection contre les failles LFI.
*   **Multi-Tenant :** Isolation totale des données par entreprise (`company_id`).
*   **Interface Moderne :** UI responsive (TailwindCSS + Alpine.js) avec support RTL (Right-to-Left) natif.
*   **Partage Instantané :** Envoi des commandes par WhatsApp et Email en un clic.

---

## 🚀 Démarrage Rapide (Local)

### 1. Cloner et Installer
```bash
git clone https://github.com/votre-org/btp-commande.git
cd btp-commande
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialiser la Base de Données
Le script crée les tables et un administrateur par défaut.
```bash
python init_db.py
```
*Compte Admin par défaut : `admin@btpcommande.ma` / `admin123`*

### 3. Lancer l'Application
```bash
flask run
```
Accédez à `http://127.0.0.1:5000`.

---

## 🛠️ Stack Technique

*   **Backend :** Python 3.12, Flask 3.0, SQLAlchemy 2.0.
*   **Frontend :** Jinja2 (SSR), TailwindCSS (CDN), Alpine.js.
*   **PDF Engine :** WeasyPrint 68.0 (Requiert `libpango`, `libcairo`).
*   **Base de Données :** SQLite (Dev), PostgreSQL (Prod).
*   **Sécurité :** Flask-Login, Flask-WTF (CSRF), Secure Headers.

---

## 🧪 Tests

Pour lancer la suite de tests unitaires et d'intégration :
```bash
pytest
```

---

## 👥 Crédits

*   **Produit de :** MOA Digital Agency (www.myoneart.com)
*   **Développement :** Aisance KALONJI (www.aisancekalonji.com)
*   **Audit Sécurité :** La CyberConfiance (www.cyberconfiance.com)
*   **Documentation & Refonte :** Jules (Lead Dev)

---
&copy; 2024 BTP Commande. Tous droits réservés.
