#!/bin/bash

# Script d'installation des dépendances système pour BTP Commande sur VPS (Debian/Ubuntu)
# Ce script installe les librairies requises pour WeasyPrint (génération PDF)

if [ "$EUID" -ne 0 ]
  then echo "Veuillez exécuter ce script en tant que root (sudo)"
  exit
fi

echo "Mise à jour des paquets..."
apt-get update

echo "Installation des dépendances système pour WeasyPrint..."
# Dépendances basées sur la documentation officielle de WeasyPrint pour Debian/Ubuntu
# Inclut Pango, Cairo, GDK-Pixbuf, et autres librairies graphiques/fontes
apt-get install -y \
    python3-pip \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    shared-mime-info

echo "Installation des dépendances Python..."
pip install -r requirements.txt

echo "========================================================"
echo "Installation terminée avec succès !"
echo "Vous pouvez maintenant lancer l'application :"
echo "python init_db.py  # Pour initialiser la base de données"
echo "python app.py      # Pour lancer le serveur"
echo "========================================================"
