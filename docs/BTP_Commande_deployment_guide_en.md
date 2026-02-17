[ 🇫🇷 Français ](BTP_Commande_deployment_guide.md) | [ 🇬🇧 **English** ](BTP_Commande_deployment_guide_en.md)

# BTP Commande - Deployment Guide

This guide details the procedures for installing **BTP Commande** in a local development environment and on a production server (Linux VPS).

---

## 1. System Requirements

*   **OS:** Ubuntu 20.04/22.04 LTS (Recommended) or macOS/Windows (WSL2).
*   **Python:** 3.10 or higher.
*   **Database:** SQLite (Dev), PostgreSQL (Prod).
*   **System Dependencies:** `libcairo2`, `libpango-1.0-0` (For WeasyPrint).

---

## 2. Local Installation (Dev)

### 2.1 Clone Repository
```bash
git clone <private-repo-url>
cd btp-commande
```

### 2.2 Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.3 Configuration
Create a `.env` file at the root:
```ini
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=dev-key-change-me
DATABASE_URL=sqlite:///btp_commande.db
```

### 2.4 Initialize DB
```bash
python init_db.py
```
*Creates tables and a default admin account (admin@btpcommande.ma / admin123).*

### 2.5 Run Server
```bash
flask run
```
Access: `http://127.0.0.1:5000`

---

## 3. Production Deployment (VPS)

### 3.1 Automated Install Script
The `setup_vps.sh` script installs necessary system packages.
```bash
chmod +x setup_vps.sh
sudo ./setup_vps.sh
```

### 3.2 Application Server (Gunicorn)
Never use `flask run` in production. Use Gunicorn.
```bash
gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"
```

### 3.3 Systemd Service
Create `/etc/systemd/system/btp-commande.service`:
```ini
[Unit]
Description=Gunicorn instance for BTP Commande
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

### 3.4 Reverse Proxy (Nginx)
Configure Nginx to handle SSL and static files.
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/btp-commande/btp.sock;
    }

    location /static {
        alias /var/www/btp-commande/static;
    }
}
```

---

## 4. Maintenance

### Updates
```bash
git fetch origin main
git merge origin/main
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
sudo systemctl restart btp-commande
```

### Logs
*   **Application:** `journalctl -u btp-commande -f`
*   **Web Server:** `/var/log/nginx/error.log`
