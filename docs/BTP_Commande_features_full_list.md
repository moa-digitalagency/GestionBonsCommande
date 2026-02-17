[ 🇫🇷 **Français** ](BTP_Commande_features_full_list.md) | [ 🇬🇧 English ](BTP_Commande_features_full_list_en.md)

# BTP Commande - Bible des Fonctionnalités

> **CONFIDENTIEL :** Ce document recense l'intégralité des règles métier et fonctionnalités de la solution BTP Commande. Usage interne MOA Digital Agency uniquement.

---

## 1. Authentification & Sécurité (RBAC)

### 1.1 Connexion
*   **Identifiants :** Email / Mot de passe.
*   **Sécurité :** Hachage via `Werkzeug` (pbkdf2:sha256).
*   **Redirection :** Automatique vers `/dashboard` après succès.
*   **Feedback :** Messages flash (Succès/Erreur) gérés par Alpine.js.

### 1.2 Gestion des Rôles (RBAC Hybride)
L'application supporte un modèle hybride pour la rétrocompatibilité :
*   **Legacy :** Champ `role` (string) sur le modèle `User`.
*   **Moderne :** Tables `Role` et `Permission` liées à `User`.
*   **Rôles Standards :**
    *   `Super Admin` : Accès total (Cross-tenant).
    *   `Admin` : Gestionnaire de l'entreprise (Tenant scope).
    *   `Valideur` : Droit de valider les commandes.
    *   `Acheteur` : Droit de créer des commandes.

### 1.3 Isolation Multi-Tenant
*   Chaque requête est interceptée par le `TenantService`.
*   Un utilisateur ne voit **que** les données (Commandes, Projets, Produits) liées à son `company_id`.
*   Exceptions : Le Super Admin peut voir toutes les données (via un dashboard spécifique ou impersonation - *feature flag*).

---

## 2. Gestion des Commandes (Core Business)

### 2.1 Cycle de Vie (State Machine)
1.  **BROUILLON (`draft`)** : Création initiale. Modifiable à volonté. Non visible par les valideurs.
2.  **SOUMIS (`submitted`)** : Envoyé pour validation. Non modifiable par le créateur.
3.  **VALIDE (`validated`)** : Approuvé par un N+1. Verrouillé. Prêt pour génération PDF.
4.  **REJETE (`rejected`)** : Retourné au créateur avec motif. Redevient modifiable.
5.  **ARCHIVE (`archived`)** : Masqué des listes courantes (Soft delete).

### 2.2 Création & Édition
*   **Sélection Chantier :** Dropdown filtré par entreprise.
*   **Date Souhaitée :** Datepicker HTML5 natif.
*   **Lignes de Commande (Alpine.js) :**
    *   Ajout dynamique de lignes sans rechargement.
    *   Champs : Description, Quantité, Unité (Liste prédéfinie : m², kg, L, u...), Prix Unitaire (Optionnel).
    *   **Auto-Traduction :** À la sauvegarde, la description est envoyée au `LexiqueService` pour pré-remplir la traduction (Ar/Dr).

### 2.3 Validation
*   Accessible uniquement aux rôles `Valideur` et `Admin`.
*   Vue détaillée avec récapitulatif des coûts.
*   Actions : `Valider` (Change statut -> Validated) ou `Rejeter` (Ouvre modale motif -> Statut Rejected).

### 2.4 Génération PDF (WeasyPrint)
*   **Trigger :** Bouton "Télécharger PDF" uniquement si statut = `VALIDE`.
*   **Moteur :** WeasyPrint 68.0+.
*   **Layout :**
    *   Header : Logo Entreprise + Info Chantier.
    *   Body : Tableau des articles (Français + Arabe).
    *   Footer : Mentions légales et signature.
*   **Stockage :** `static/uploads/pdfs/`. Nommage : `BC_{ID}_{TIMESTAMP}.pdf`.

### 2.5 Partage (Deep Links)
*   **WhatsApp :** Lien `wa.me` généré dynamiquement.
    *   Contenu : "Bonjour, voici le BC #{ref} pour le chantier {site}. Lien : {url}".
*   **Email :** Lien `mailto:` avec sujet et corps pré-remplis.

---

## 3. Dictionnaire & Traduction (Lexique)

### 3.1 Recherche Intelligente
*   **Entrée :** Terme en Français.
*   **Sortie :** Terme en Arabe (Standard) et Darija (Marocain).
*   **Algorithme :** Recherche exacte > Recherche inversée (chercher "Beton" via le mot arabe) > Alias.

### 3.2 Gestion Collaborative
*   **Suggestion :** Formulaire pour proposer un nouveau terme.
*   **Validation Admin :** Les suggestions arrivent en statut `pending`. L'admin les approuve pour les verser au dictionnaire global.

### 3.3 Import de Masse
*   Script : `scripts/import_lexique.py`.
*   Format : Excel (.xlsx) avec colonnes `Francais`, `Darija_arabe`, `Darija_latin`.
*   Performance : Upsert (Update si existe, Insert si nouveau).

---

## 4. Paramètres & Configuration

### 4.1 Numérotation des Documents
*   Configurable par entreprise (Table `Company.settings` JSON).
*   Options : Préfixe (ex: "BC-24-"), Séquence de départ, Longueur du numéro.

### 4.2 Internationalisation (i18n)
*   **Langues supportées :** Français (fr), Anglais (en), Arabe (ar), Darija (dr).
*   **RTL Support :** Si langue = `ar`, injection automatique de `dir="rtl"` et ajustement des marges Tailwind (ml/mr inversés).
*   **Stockage :** Fichiers JSON plats dans `translations/`.
*   **Service :** `I18nService` (Singleton custom, pas de Flask-Babel pour plus de légèreté).

---

## 5. Interface Utilisateur (UX/UI)

### 5.1 Design System
*   **Framework :** Tailwind CSS.
*   **Palette :**
    *   Primaire : Slate 900 (Textes), Blue 600 (Actions).
    *   Background : Slate 50 (App), White (Cards).
*   **Polices :** Inter (Latin), Cairo (Arabe).
*   **Icônes :** Lucide (SVG injectés).

### 5.2 Interactivité (Alpine.js)
*   **Modales :** `x-data="{ open: false }"`.
*   **Dropdowns :** Gestion de l'état ouverture/fermeture et click-away.
*   **Cloak :** Attribut `x-cloak` pour éviter le scintillement au chargement.
*   **Notifications :** Disparition automatique des messages flash après 5 secondes.

