# Guide de Déploiement Manuel sur VPS (sans Docker)

Ce guide décrit la procédure pour installer et configurer l'application BTP Commande sur un VPS Linux (Debian/Ubuntu) manuellement.

## Prérequis

*   Un VPS avec Ubuntu 20.04+ ou Debian 11+.
*   Accès root ou sudo.
*   Python 3.8+ installé (généralement par défaut).

## Installation

### 1. Cloner le dépôt
Récupérez le code source de l'application sur votre serveur.
```bash
git clone <votre-repo-url>
cd btp-commande
```

### 2. Exécuter le script d'installation
Ce script va installer les dépendances système (nécessaires pour WeasyPrint) et créer un environnement virtuel Python.

```bash
sudo ./setup_vps.sh
```
*Note : Si le script n'est pas exécutable, lancez `chmod +x setup_vps.sh`.*

### 3. Activer l'environnement virtuel
Une fois l'installation terminée, activez l'environnement virtuel pour toutes les commandes suivantes :

```bash
source venv/bin/activate
```
*(Votre invite de commande devrait afficher `(venv)`).*

### 4. Configuration
Vérifiez le fichier `config/settings.py` ou définissez les variables d'environnement nécessaires (ex: `DATABASE_URL`, `SECRET_KEY`).
Pour un test rapide avec SQLite, la configuration par défaut suffit.

### 5. Initialiser la base de données
Cette commande crée les tables et le compte Super Admin par défaut.

```bash
python init_db.py
```
*Super Admin par défaut : `admin@btpcommande.ma` / `admin123`*

### 6. Lancer l'application
Pour un test de développement :
```bash
python app.py
```

Pour la production, utilisez `gunicorn` :
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Dépannage

*   **Erreur WeasyPrint / DLL load failed :** Assurez-vous d'avoir exécuté `./setup_vps.sh` avec `sudo` pour installer `libcairo2` et `libpango`.
*   **ModuleNotFoundError :** Vérifiez que votre environnement virtuel est activé (`source venv/bin/activate`).
