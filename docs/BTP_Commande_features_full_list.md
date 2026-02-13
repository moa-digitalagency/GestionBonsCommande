# BTP Commande - Liste Exhaustive des Fonctionnalités (Bible)

Ce document recense l'intégralité des fonctionnalités techniques et métier de l'application **BTP Commande**. Il sert de référence pour les développeurs, les chefs de projet et les équipes QA.

---

## 1. Authentification & Sécurité (Auth Module)

L'application sécurise l'accès via un système d'authentification robuste basé sur `Flask-Login` et des protections contre les vulnérabilités courantes.

### 1.1 Gestion des Identifiants
*   **Hachage des Mots de Passe :** Utilisation de l'algorithme `PBKDF2` avec `SHA256` (via `werkzeug.security`) pour le stockage sécurisé.
*   **Session Utilisateur :**
    *   Durée de vie configurable (défaut : 24 heures).
    *   Protection `HttpOnly` et `SameSite=Lax` pour les cookies de session.
    *   Renouvellement automatique (`fresh_login_required` pour les actions sensibles).
*   **Protection CSRF :** Tous les formulaires (`Flask-WTF`) incluent un jeton CSRF obligatoire pour prévenir les attaques Cross-Site Request Forgery.

### 1.2 Contrôle d'Accès (RBAC Hybride)
L'application utilise un système hybride de rôles :
*   **Rôles Legacy (String) :** `super_admin`, `admin`, `valideur`, `demandeur`. Utilisé pour la compatibilité descendante.
*   **RBAC Moderne (Modèles) :**
    *   **Entité `Role` :** Définit un groupe de permissions (ex: "Super Admin", "Chef de Chantier").
    *   **Entité `Permission` :** Granularité fine (ex: `manage_users`, `validate_orders`).
    *   **Vérification :** Le décorateur `@tenant_required` assure l'isolation des données par entreprise (`company_id`).

---

## 2. Gestion des Bons de Commande (Order Module)

Cœur du métier, ce module gère le cycle de vie complet d'un achat, de la demande à la validation finale.

### 2.1 Cycle de Vie (Workflow d'État)
Les commandes suivent une machine à états stricte (`models.order.Order`) :
1.  **BROUILLON :** Création par un `demandeur`. Modifiable uniquement par le créateur ou un admin.
2.  **SOUMIS :** Verrouillage pour le demandeur. En attente de validation par un `valideur` ou `admin`.
3.  **VALIDE :** Approuvé par un valideur. Déclenche la possibilité de générer le PDF.
4.  **PDF_GENERE :** Le document officiel est créé et stocké.
5.  **PARTAGE :** Le bon a été envoyé au fournisseur (WhatsApp/Email).
6.  *(Optionnel)* **REJETE :** Retour au demandeur avec motif du refus.

### 2.2 Création et Édition
*   **Sélection Chantier :** Obligatoire. Filtrée par les droits de l'utilisateur (Multi-tenant).
*   **Lignes de Commande :**
    *   Ajout dynamique via AJAX/HTMX (ou rechargement).
    *   Support des unités variées (`m²`, `kg`, `unite`, `L`, etc.).
    *   **Traduction Automatique :** Lors de l'ajout d'une ligne, la description est automatiquement traduite via le `LexiqueService` pour faciliter la communication avec les fournisseurs.
*   **Notes Multilingues :** Champs séparés pour les notes internes et les notes fournisseurs (FR/EN).

### 2.3 Génération de PDF (Moteur WeasyPrint)
*   **Technologie :** Rendu HTML/CSS vers PDF via `WeasyPrint` (version 68.0+).
*   **Sécurité LFI (Local File Inclusion) :** Utilisation d'un `safe_url_fetcher` personnalisé qui interdit strictement l'accès aux fichiers locaux en dehors du dossier `statics/`.
*   **Mise en Page :**
    *   Format A4.
    *   En-tête avec Logo Entreprise et Informations Chantier.
    *   Tableau des articles avec totaux.
    *   Pied de page légal.
*   **Stockage :** Les PDFs générés sont sauvegardés dans `statics/uploads/pdfs/` avec un nommage unique (`BC_{numero}_{timestamp}.pdf`).

### 2.4 Partage (Deep Linking)
*   **WhatsApp :** Génération d'un lien `wa.me` avec un message pré-rempli contenant : Numéro BC, Chantier, Date souhaitée, Liste des articles (Quantité + Unité).
*   **Email :** Génération d'un lien `mailto:` avec sujet et corps pré-remplis.
*   **Tracking :** L'action de partage met à jour l'état de la commande et enregistre l'horodatage (`shared_at`).

---

## 3. Dictionnaire Intelligent (Lexique Module)

Système centralisé de traduction technique BTP (Bâtiment et Travaux Publics) pour standardiser les termes entre les ingénieurs et les fournisseurs.

### 3.1 Moteur de Recherche (Fuzzy Logic)
Le `LexiqueService` utilise un algorithme de recherche pondéré pour trouver la meilleure correspondance :
1.  **Correspondance Exacte (Score 1.0) :** Le terme existe tel quel dans la base.
2.  **Traduction Inverse (Score 0.8) :** Le terme cherché correspond à une traduction existante (ex: chercher "Ciment" trouve l'entrée via sa traduction Arabe).
3.  **Alias (Score 0.7) :** Correspondance sur des synonymes ou termes argotiques définis.

### 3.2 Importation en Masse
*   **Format Supporté :** Fichiers Excel (`.xlsx`).
*   **Script :** `scripts/import_lexique.py`.
*   **Logique :**
    *   Mappe les colonnes `Francais`, `Darija_arabe`, `Darija_latin` aux codes langues `fr`, `ar`, `dr`.
    *   Mode "Upsert" : Met à jour les entrées existantes (basé sur le terme français) et crée les nouvelles.
    *   Performance : Pré-chargement des entrées en mémoire pour éviter les requêtes N+1.

### 3.3 Suggestions Collaboratives
*   Les utilisateurs peuvent proposer de nouvelles traductions si un terme est introuvable.
*   **Workflow de Validation :**
    *   Statut `pending` par défaut.
    *   Interface d'administration pour `Approuver` (crée une entrée officielle) ou `Rejeter` la suggestion.

---

## 4. Internationalisation (i18n) & UX

### 4.1 Support RTL (Right-to-Left)
*   Détection automatique basée sur la locale courante (`ar`).
*   Injection dynamique de l'attribut `dir="rtl"` sur la balise `<html>`.
*   Utilisation de la police **Cairo** pour les textes arabes et **Inter** pour les textes latins (via classes utilitaires Tailwind `font-arabic`).

### 4.2 Traductions
*   Service : `I18nService` (Singleton).
*   Stockage : Fichiers JSON dans le dossier `translations/`.
*   Fallback : Si une clé de traduction est manquante, la clé elle-même est affichée (souvent le texte français).

### 4.3 Interface Utilisateur (Tailwind & Alpine)
*   **Responsive Design :** Sidebar rétractable sur mobile, tableaux adaptatifs (colonnes masquées sur petits écrans).
*   **Interactivité :** Alpine.js gère les états locaux (modales, dropdowns, fermeture des alertes) sans rechargement de page.
*   **Anti-Flicker :** Utilisation de l'attribut `x-cloak` pour masquer les composants non initialisés.

---

## 5. Administration & Configuration

### 5.1 Multi-Tenant (Isolation)
*   Chaque utilisateur est lié à une `Company`.
*   Le `TenantService` filtre automatiquement toutes les requêtes (Commandes, Projets, Produits) pour ne retourner que les données de l'entreprise de l'utilisateur connecté.

### 5.2 Paramètres Globaux
*   Configuration via `config/settings.py` et variables d'environnement (`.env`).
*   **Settings Dynamiques :** La table `site_settings` permet de configurer le titre du site, le logo, et les méta-données SEO sans redéploiement.

---

## 6. Stack Technique Résumé

| Composant | Technologie | Détail |
| :--- | :--- | :--- |
| **Backend** | Python / Flask | Blueprints, App Factory Pattern |
| **ORM** | SQLAlchemy | Support SQLite (Dev) & PostgreSQL (Prod) |
| **Frontend** | Jinja2 + TailwindCSS | Rendu serveur avec utilitaires CSS modernes |
| **JS Framework** | Alpine.js | Léger, pour l'interactivité UI |
| **PDF Engine** | WeasyPrint | Rendu fidèle du HTML/CSS |
| **Icons** | Lucide | SVG injectés dynamiquement |
