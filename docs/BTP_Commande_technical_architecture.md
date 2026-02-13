# BTP Commande - Architecture Technique

Ce document détaille l'architecture logicielle, la structure de la base de données et les choix techniques structurants du projet **BTP Commande**.

---

## 1. Structure du Projet (Flask Application Factory)

Le projet suit le pattern "Application Factory" recommandé par Flask pour une meilleure testabilité et modularité.

### 1.1 Arborescence Principale
```
.
├── app.py                  # Point d'entrée (Factory create_app)
├── config/                 # Configuration (Dev, Prod, Testing)
├── models/                 # Modèles SQLAlchemy (ORM)
├── routes/                 # Contrôleurs (Blueprints)
├── services/               # Logique Métier (Service Layer)
├── static/                 # Assets (CSS, JS, Uploads)
├── templates/              # Vues Jinja2
└── tests/                  # Tests unitaires et d'intégration
```

### 1.2 Initialisation (`app.py`)
La fonction `create_app` est responsable de :
1.  Charger la configuration depuis `config.settings.Config`.
2.  Initialiser les extensions : `db` (SQLAlchemy), `login_manager` (Auth), `csrf` (WTF), `i18n`.
3.  Enregistrer les Blueprints (`auth`, `orders`, `lexique`, etc.).
4.  Injecter les variables globales dans les templates (ex: `current_user`, `settings`).

---

## 2. Modèle de Données (Schema Database)

L'application utilise SQLAlchemy comme ORM. La base de données par défaut est SQLite, mais le schéma est compatible PostgreSQL.

### 2.1 Entités Principales

#### `User` (Utilisateurs)
*   `id`, `email`, `password_hash`, `role` (legacy), `role_id` (RBAC).
*   Relations : `company` (Multi-tenant), `orders_created`.

#### `Company` (Entreprises)
*   `id`, `name`, `logo_url`.
*   `settings` (JSON) : Contient la configuration du moteur de numérotation des bons de commande.

#### `Order` (Commandes)
*   `bc_number` : Numéro unique généré séquentiellement.
*   `status` : Machine à état (`BROUILLON`, `SOUMIS`, `VALIDE`, `PDF_GENERE`).
*   `pdf_path` : Chemin relatif vers le fichier généré.
*   Relations : `lines` (Lignes de commande), `history` (Audit log).

#### `OrderLine` (Lignes)
*   `description` : Texte libre ou issu du catalogue.
*   `quantity`, `unit`, `unit_price`.
*   `description_translated` : Traduction figée au moment de la création.

#### `LexiqueEntry` (Dictionnaire)
*   `category` : Catégorie métier (ex: 'Maçonnerie').
*   `translations` (JSON ?) ou Colonnes dédiées (`fr`, `ar`, `dr`).
*   `usage_count` : Compteur pour le tri par popularité.

---

## 3. Couche de Services (Business Logic)

L'application isole la logique métier dans le dossier `services/` pour garder les contrôleurs (`routes/`) légers.

### 3.1 `TenantService` (Multi-tenant)
*   **Rôle :** Assure que les données retournées appartiennent toujours à l'entreprise de l'utilisateur connecté.
*   **Méthode clé :** `get_tenant_orders()` filtre automatiquement sur `company_id`.

### 3.2 `PDFService` (Génération Documentaire)
*   **Moteur :** WeasyPrint (HTML/CSS -> PDF).
*   **Sécurité (LFI) :** Implémente un `safe_url_fetcher` personnalisé qui rejette toute requête `file://` pointant hors du dossier `statics/`. Cela empêche la lecture arbitraire de fichiers système via l'injection HTML.
*   **Dépendances :** Requiert les librairies système `libpango`, `libcairo` (voir script d'installation).

### 3.3 `LexiqueService` (Recherche & Traduction)
*   **Algorithme :** Recherche floue (Fuzzy Search) pondérée.
    *   Match exact > Traduction > Alias.
*   **Import :** Traitement par lots (Batch processing) des fichiers Excel pour l'alimentation initiale.

---

## 4. Architecture Frontend

### 4.1 Rendu Serveur (Server-Side Rendering)
*   Utilisation de **Jinja2** pour le templating HTML.
*   Héritage de templates : `base.html` définit la structure globale (Header, Sidebar, Footer).

### 4.2 Styles (TailwindCSS)
*   Intégration via CDN (pour le développement rapide, à compiler pour la prod).
*   Configuration étendue dans `base.html` :
    *   Couleurs personnalisées (`brand`, `slate`).
    *   Polices : **Inter** (Latin) et **Cairo** (Arabe).
*   Support RTL : Classes dynamiques `dir="rtl"` et utilitaires `text-right` pour l'arabe.

### 4.3 Interactivité (Alpine.js)
*   Framework JS léger pour la logique UI (Modales, Dropdowns, Fermeture d'alertes).
*   **Directives clés :** `x-data`, `x-show`, `x-transition`.
*   **Performance :** Utilisation de `x-cloak` pour éviter le "Flash of Unstyled Content" (FOUC).

---

## 5. Sécurité

1.  **CSRF (Cross-Site Request Forgery) :**
    *   Protection globale via `Flask-WTF`.
    *   Token injecté dans tous les formulaires POST et dans les headers AJAX (`X-CSRFToken`).

2.  **Gestion des Sessions :**
    *   Cookies `HttpOnly` pour empêcher le vol de session via XSS.
    *   Configuration `PERMANENT_SESSION_LIFETIME` stricte.

3.  **Uploads Sécurisés :**
    *   Validation des extensions de fichiers (`ALLOWED_EXTENSIONS`).
    *   Nettoyage des noms de fichiers via `werkzeug.utils.secure_filename`.
