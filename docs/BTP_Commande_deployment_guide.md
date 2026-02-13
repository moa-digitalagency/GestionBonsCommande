# BTP Commande - Guide de Déploiement & Installation

Ce guide détaille les étapes pour installer, configurer et déployer l'application **BTP Commande** en environnement local (développement) et sur un serveur VPS (production).

---

## 1. Prérequis Système

Avant de commencer, assurez-vous de disposer de l'environnement suivant :

*   **OS :** Linux (Ubuntu 20.04/22.04 recommandé) ou macOS/Windows (WSL2).
*   **Python :** Version 3.10 ou supérieure (Testé avec 3.12).
*   **Base de Données :** SQLite (Défaut Dev) ou PostgreSQL (Recommandé Prod).
*   **Librairies Système :** Nécessaires pour `WeasyPrint` (Génération PDF).
    *   `libcairo2`, `libpango-1.0-0`, `libgdk-pixbuf2.0-0`.

---

## 2. Installation Locale (Développement)

Pour contribuer au projet ou tester localement :

### 2.1 Cloner le Dépôt
```bash
git clone <url-du-repo>
cd btp-commande
```

### 2.2 Créer l'Environnement Virtuel
Il est impératif d'utiliser un environnement virtuel pour isoler les dépendances Python.
```bash
# Création
python3 -m venv venv

# Activation (Linux/macOS)
source venv/bin/activate

# Activation (Windows)
venv\Scripts\activate
```

### 2.3 Installer les Dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
*Si l'installation de WeasyPrint échoue sous Windows, installez GTK3 Runtime.*

### 2.4 Configuration Environnement
Créez un fichier `.env` à la racine (copiez `.env.example` s'il existe) :
```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-me
DATABASE_URL=sqlite:///btp_commande.db
```

### 2.5 Initialiser la Base de Données
Le script `init_db.py` crée les tables et injecte les données initiales (Rôles, Admin par défaut).
```bash
python init_db.py
```

### 2.6 Lancer le Serveur
```bash
flask run
# L'application sera accessible sur http://127.0.0.1:5000
```

---

## 3. Déploiement VPS (Production)

Pour un déploiement sur un serveur Linux (Ubuntu/Debian).

### 3.1 Préparation du Serveur (Automatisée)
Le script `setup_vps.sh` installe toutes les dépendances système requises (Pango, Cairo, etc.) et configure le venv.

```bash
# Rendre le script exécutable
chmod +x setup_vps.sh

# Exécuter en tant que root (sudo)
sudo ./setup_vps.sh
```

### 3.2 Configuration Production
Créez un fichier `.env` sécurisé pour la production :

```ini
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=<GENERER_UNE_CLE_FORTE_ICI>
DATABASE_URL=postgresql://user:password@localhost/btp_db
SUPER_ADMIN_EMAIL=admin@votre-domaine.com
SUPER_ADMIN_PASSWORD=<MOT_DE_PASSE_FORT>
```

### 3.3 Serveur d'Application (Gunicorn)
Ne jamais utiliser `flask run` en production. Utilisez Gunicorn (déjà dans `requirements.txt`).

```bash
# Lancer Gunicorn avec 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Pour pérenniser le processus, configurez un service Systemd :
`/etc/systemd/system/btp-commande.service`
```ini
[Unit]
Description=Gunicorn instance to serve BTP Commande
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/btp-commande
Environment="PATH=/var/www/btp-commande/venv/bin"
ExecStart=/var/www/btp-commande/venv/bin/gunicorn --workers 3 --bind unix:btp.sock -m 007 "app:create_app()"

[Install]
WantedBy=multi-user.target
```

### 3.4 Serveur Web (Nginx)
Configurez Nginx comme Reverse Proxy pour gérer SSL et les fichiers statiques.

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/btp-commande/btp.sock;
    }

    location /static {
        alias /var/www/btp-commande/statics;
    }
}
```

---

## 4. Maintenance & Mises à Jour

### Mettre à jour le code
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python init_db.py  # Applique les migrations idempotentes
sudo systemctl restart btp-commande
```

### Logs & Debugging
*   **Logs Application :** Configurés pour sortir sur `stdout`/`stderr`, capturés par Systemd/Journald.
    *   `journalctl -u btp-commande -f`
*   **Logs WeasyPrint :** Si la génération PDF échoue, vérifiez l'installation de `libcairo2`.
