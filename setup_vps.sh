#!/bin/bash

# /* * Nom de l'application : BTP Commande
#  * Description : Script d'installation VPS
#  * Produit de : MOA Digital Agency, www.myoneart.com
#  * Fait par : Aisance KALONJI, www.aisancekalonji.com
#  * Auditer par : La CyberConfiance, www.cyberconfiance.com
#  */

# Script d'installation des dépendances système pour BTP Commande sur VPS (Debian/Ubuntu)
# Ce script installe les librairies requises pour WeasyPrint (génération PDF) et configure l'environnement Python.

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
    python3-venv \
    python3-cffi \
    python3-brotli \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    libjpeg-dev \
    libopenjp2-7-dev \
    libffi-dev \
    shared-mime-info \
    libcairo2 \
    libgdk-pixbuf2.0-0

echo "Création de l'environnement virtuel (venv)..."
# Créer le venv s'il n'existe pas
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Environnement virtuel créé."
else
    echo "L'environnement virtuel existe déjà."
fi

echo "Installation des dépendances Python dans le venv..."
# Utiliser pip du venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# Ajustement des permissions pour que l'utilisateur non-root puisse utiliser le venv si le script est lancé en root
# On suppose que le répertoire courant appartient à l'utilisateur qui déploie
if [ -n "$SUDO_USER" ]; then
    chown -R $SUDO_USER:$SUDO_USER venv
fi

echo "========================================================"
echo "Installation terminée avec succès !"
echo "Vous pouvez maintenant lancer l'application :"
echo "source venv/bin/activate"
echo "python init_db.py  # Pour initialiser la base de données"
echo "python app.py      # Pour lancer le serveur"
echo ""
echo "Note : Assurez-vous d'activer l'environnement virtuel avant de lancer les commandes."
echo "========================================================"
