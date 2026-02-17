[ 🇫🇷 Français ](BTP_Commande_technical_architecture.md) | [ 🇬🇧 **English** ](BTP_Commande_technical_architecture_en.md)

# BTP Commande - Technical Architecture

This document details the software architecture, database structure, and key technical choices of the **BTP Commande** project.

---

## 1. Project Structure (Flask Application Factory)

The project follows the "Application Factory" pattern recommended by Flask for better testability and modularity.

### 1.1 Main Tree
```
.
├── app.py                  # Entry Point (Factory create_app)
├── config/                 # Configuration (Dev, Prod, Testing)
├── models/                 # SQLAlchemy Models (ORM)
├── routes/                 # Controllers (Blueprints)
├── services/               # Business Logic (Service Layer)
├── static/                 # Assets (CSS, JS, Uploads)
├── templates/              # Jinja2 Views (SSR)
└── tests/                  # Unit and Integration Tests
```

### 1.2 Initialization (`app.py`)
The `create_app` function is responsible for:
1.  Loading configuration from `config.settings.Config`.
2.  Initializing extensions: `db` (SQLAlchemy), `login_manager` (Auth), `csrf` (WTF), `i18n`.
3.  Registering Blueprints (`auth`, `orders`, `lexique`, etc.).
4.  Injecting global variables into templates (e.g., `current_user`, `settings`).

---

## 2. Data Model (Database Schema)

The application uses SQLAlchemy as ORM. The default database is SQLite, but the schema is PostgreSQL compatible.

### 2.1 Key Entities

#### `User`
*   `id`, `email`, `password_hash`, `role` (legacy), `role_id` (RBAC).
*   Relations: `company` (Multi-tenant), `orders_created`.

#### `Company`
*   `id`, `name`, `logo_url`.
*   `settings` (JSON): Contains configuration for the PO numbering engine.

#### `Order`
*   `bc_number`: Unique sequentially generated number.
*   `status`: State machine (`DRAFT`, `SUBMITTED`, `VALIDATED`, `PDF_GENERATED`).
*   `pdf_path`: Relative path to the generated file.
*   Relations: `lines` (Order lines), `history` (Audit log).

#### `OrderLine`
*   `description`: Free text or from catalog.
*   `quantity`, `unit`, `unit_price`.
*   `description_translated`: Frozen translation at creation time.

#### `LexiqueEntry` (Dictionary)
*   `category`: Business category (e.g., 'Masonry').
*   `translations`: Dedicated columns (`fr`, `ar`, `dr`).
*   `usage_count`: Counter for sorting by popularity.

---

## 3. Service Layer (Business Logic)

The application isolates business logic in the `services/` folder to keep controllers (`routes/`) lightweight.

### 3.1 `TenantService` (Multi-tenant)
*   **Role:** Ensures that returned data always belongs to the logged-in user's company.
*   **Key Method:** `get_tenant_orders()` automatically filters on `company_id`.

### 3.2 `PDFService` (Document Generation)
*   **Engine:** WeasyPrint (HTML/CSS -> PDF).
*   **Security (LFI):** Implements a custom `safe_url_fetcher` that rejects any `file://` request pointing outside the `statics/` folder. This prevents arbitrary file reading via HTML injection.
*   **Dependencies:** Requires system libraries `libpango`, `libcairo` (see installation script).

### 3.3 `LexiqueService` (Search & Translation)
*   **Algorithm:** Weighted Fuzzy Search.
    *   Exact Match > Translation > Alias.
*   **Import:** Batch processing of Excel files for initial seeding.

---

## 4. Frontend Architecture

### 4.1 Server-Side Rendering
*   Use of **Jinja2** for HTML templating.
*   Template inheritance: `base.html` defines the global structure (Header, Sidebar, Footer).

### 4.2 Styles (TailwindCSS)
*   Integration via CDN (for rapid development, compile for prod).
*   Extended configuration in `base.html`:
    *   Custom colors (`brand`, `slate`).
    *   Fonts: **Inter** (Latin) and **Cairo** (Arabic).
*   RTL Support: Dynamic classes `dir="rtl"` and utilities `text-right` for Arabic.

### 4.3 Interactivity (Alpine.js)
*   Lightweight JS framework for UI logic (Modals, Dropdowns, Alert closing).
*   **Key Directives:** `x-data`, `x-show`, `x-transition`.
*   **Performance:** Use of `x-cloak` to avoid "Flash of Unstyled Content" (FOUC).

---

## 5. Security

1.  **CSRF (Cross-Site Request Forgery):**
    *   Global protection via `Flask-WTF`.
    *   Token injected in all POST forms and AJAX headers (`X-CSRFToken`).

2.  **Session Management:**
    *   `HttpOnly` cookies to prevent session theft via XSS.
    *   Strict `PERMANENT_SESSION_LIFETIME` configuration.

3.  **Secure Uploads:**
    *   File extension validation (`ALLOWED_EXTENSIONS`).
    *   Filename sanitization via `werkzeug.utils.secure_filename`.
