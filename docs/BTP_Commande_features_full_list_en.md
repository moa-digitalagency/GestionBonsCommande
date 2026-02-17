[ 🇫🇷 Français ](BTP_Commande_features_full_list.md) | [ 🇬🇧 **English** ](BTP_Commande_features_full_list_en.md)

# BTP Commande - Feature Bible

> **CONFIDENTIAL:** This document lists all business rules and features of the BTP Commande solution. Internal use MOA Digital Agency only.

---

## 1. Authentication & Security (RBAC)

### 1.1 Login
*   **Credentials:** Email / Password.
*   **Security:** Hashing via `Werkzeug` (pbkdf2:sha256).
*   **Redirect:** Automatic to `/dashboard` upon success.
*   **Feedback:** Flash messages (Success/Error) managed by Alpine.js.

### 1.2 Role Management (Hybrid RBAC)
The application supports a hybrid model for backward compatibility:
*   **Legacy:** `role` field (string) on the `User` model.
*   **Modern:** `Role` and `Permission` tables linked to `User`.
*   **Standard Roles:**
    *   `Super Admin`: Full access (Cross-tenant).
    *   `Admin`: Company manager (Tenant scope).
    *   `Validator`: Right to validate orders.
    *   `Buyer`: Right to create orders.

### 1.3 Multi-Tenant Isolation
*   Every request is intercepted by the `TenantService`.
*   A user sees **only** data (Orders, Projects, Products) linked to their `company_id`.
*   Exceptions: Super Admin can view all data (via a specific dashboard or impersonation - *feature flag*).

---

## 2. Order Management (Core Business)

### 2.1 Lifecycle (State Machine)
1.  **DRAFT (`draft`)**: Initial creation. Editable at will. Not visible to validators.
2.  **SUBMITTED (`submitted`)**: Sent for validation. Not editable by creator.
3.  **VALIDATED (`validated`)**: Approved by N+1. Locked. Ready for PDF generation.
4.  **REJECTED (`rejected`)**: Returned to creator with reason. Becomes editable again.
5.  **ARCHIVED (`archived`)**: Hidden from current lists (Soft delete).

### 2.2 Creation & Editing
*   **Site Selection:** Dropdown filtered by company.
*   **Desired Date:** Native HTML5 datepicker.
*   **Order Lines (Alpine.js):**
    *   Dynamic addition of lines without reload.
    *   Fields: Description, Quantity, Unit (Predefined list: m², kg, L, u...), Unit Price (Optional).
    *   **Auto-Translation:** On save, the description is sent to `LexiqueService` to pre-fill the translation (Ar/Dr).

### 2.3 Validation
*   Accessible only to `Validator` and `Admin` roles.
*   Detailed view with cost summary.
*   Actions: `Validate` (Changes status -> Validated) or `Reject` (Opens reason modal -> Status Rejected).

### 2.4 PDF Generation (WeasyPrint)
*   **Trigger:** "Download PDF" button only if status = `VALIDATED`.
*   **Engine:** WeasyPrint 68.0+.
*   **Layout:**
    *   Header: Company Logo + Site Info.
    *   Body: Table of items (French + Arabic).
    *   Footer: Legal notices and signature.
*   **Storage:** `static/uploads/pdfs/`. Naming: `BC_{ID}_{TIMESTAMP}.pdf`.

### 2.5 Sharing (Deep Links)
*   **WhatsApp:** Dynamically generated `wa.me` link.
    *   Content: "Hello, here is PO #{ref} for site {site}. Link: {url}".
*   **Email:** `mailto:` link with pre-filled subject and body.

---

## 3. Dictionary & Translation (Lexique)

### 3.1 Smart Search
*   **Input:** Term in French.
*   **Output:** Term in Arabic (Standard) and Darija (Moroccan).
*   **Algorithm:** Exact Match > Reverse Search (search "Beton" via Arabic word) > Alias.

### 3.2 Collaborative Management
*   **Suggestion:** Form to propose a new term.
*   **Admin Validation:** Suggestions arrive in `pending` status. Admin approves them to add to the global dictionary.

### 3.3 Bulk Import
*   Script: `scripts/import_lexique.py`.
*   Format: Excel (.xlsx) with columns `Francais`, `Darija_arabe`, `Darija_latin`.
*   Performance: Upsert (Update if exists, Insert if new).

---

## 4. Settings & Configuration

### 4.1 Document Numbering
*   Configurable per company (`Company.settings` JSON table).
*   Options: Prefix (e.g., "BC-24-"), Start Sequence, Number Length.

### 4.2 Internationalization (i18n)
*   **Supported Languages:** French (fr), English (en), Arabic (ar), Darija (dr).
*   **RTL Support:** If language = `ar`, automatic injection of `dir="rtl"` and Tailwind margin adjustment (ml/mr inverted).
*   **Storage:** Flat JSON files in `translations/`.
*   **Service:** `I18nService` (Custom Singleton, no Flask-Babel for lightweight).

---

## 5. User Interface (UX/UI)

### 5.1 Design System
*   **Framework:** Tailwind CSS.
*   **Palette:**
    *   Primary: Slate 900 (Texts), Blue 600 (Actions).
    *   Background: Slate 50 (App), White (Cards).
*   **Fonts:** Inter (Latin), Cairo (Arabic).
*   **Icons:** Lucide (Injected SVGs).

### 5.2 Interactivity (Alpine.js)
*   **Modals:** `x-data="{ open: false }"`.
*   **Dropdowns:** Management of open/close state and click-away.
*   **Cloak:** `x-cloak` attribute to prevent flicker on load.
*   **Notifications:** Automatic disappearance of flash messages after 5 seconds.
