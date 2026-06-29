# Tanu's Collection — Backend Development Log

**Project:** Inventory & catalog system for a family-owned saree business (est. 2012)
**Stack:** Django + Django REST Framework + MySQL + React (frontend, later)
**Approach:** Backend-first, milestone-by-milestone, mentor-style review

---

## Milestone 1: Backend Planning

### Architecture Decision
**Monolith, not microservices.** With ~5-6 entities and one primary admin user (business owner), microservices would add deployment complexity with zero benefit at this scale. We keep clean internal app boundaries instead, so extraction later (if ever needed) is possible without a rewrite.

### Project & App Structure
```
tanus-collection-backend/
├── config/                        ← renamed from project name to avoid
│   │                                 nested-folder/import confusion
│   ├── settings/
│   │   ├── base.py                ← shared settings
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── catalog/                   ← Category, Product, ProductImage
│   │   ├── models.py
│   │   ├── admin.py
│   │   ├── services.py            ← business logic lives here
│   │   └── signals.py
│   ├── inquiries/                 ← Inquiry (WhatsApp click logging)
│   ├── activity_log/              ← ActivityLog (audit trail)
│   └── core/                      ← shared base models/utilities
│
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── .env / .env.example
└── .gitignore
```

**Key reasoning:**
- `catalog` bundles Category + Product + ProductImage as one cohesive bounded context (tightly coupled). Inquiry and ActivityLog get separate apps since they reference Product but aren't part of its core domain.
- `services.py` per app implements the **Service Layer pattern** — business logic lives here, not in views, bloated models, or serializers, so it's reusable across admin, APIs, and signals.

### Dependency Planning
- **Base:** `django`, `djangorestframework`, `mysqlclient`, `django-environ`, `Pillow`
- **Development only:** `django-debug-toolbar`, `ipython`
- **Production only:** `gunicorn`, `whitenoise`
- JWT (`djangorestframework-simplejwt`) deliberately deferred — not needed until V1 customer-facing APIs are built (premature otherwise).

### MySQL Setup Strategy
- Local dev DB: `tanus_collection_dev`, separate from production.
- Charset: `utf8mb4` with `utf8mb4_unicode_ci` collation (Unicode correctness for Hindi/transliterated names — `utf8` is insufficient).
- Note: on MySQL 8.0+, `utf8mb4_0900_ai_ci` is the newer default collation; `utf8mb4_unicode_ci` still works correctly, just slightly legacy.

### Environment Variables
`.env` (gitignored, real secrets) + `.env.example` (committed template, no real values). Required vars: `SECRET_KEY`, `DEBUG`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `ALLOWED_HOSTS`.

### Git Strategy
- One repo for backend, separate repo for frontend later (independent deploy lifecycles).
- `main` + feature branches (`feature/category-model`, etc.) — GitFlow considered overkill for a solo project.
- Conventional Commits style: `chore:`, `feat:`, `fix:`, etc.

### Roadmap
Planning → Setup → DB Design → Models → Admin → Business Logic → API Design → REST APIs → Testing → Optimization.

---

## Milestone 2: Project Setup

### Steps Completed
1. **Virtual environment** created and activated (`venv`) — isolates dependencies per project.
2. **Requirements files** split into `base.txt` / `development.txt` / `production.txt`, using open version ranges (`>=X,<Y`) for patch flexibility without breaking changes.
3. **Django project created**: `django-admin startproject config .` (trailing `.` avoids doubled nested folders).
4. **Settings split** into `base.py` / `development.py` / `production.py` under `config/settings/`.
5. **`.env` setup** with `django-environ` for secrets and config, `.env.example` committed as a template.
6. **`.gitignore`** created early: `venv/`, `__pycache__/`, `*.pyc`, `.env`, `media/`, `db.sqlite3`.

### MySQL Connection
- Confirmed local MySQL 8.0.44, connecting as `root@localhost` (root acceptable for local dev; production will use a least-privilege dedicated DB user).
- Created dev database manually:
  ```sql
  CREATE DATABASE tanus_collection_dev
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
  ```

### `mysqlclient` on Windows
Installed cleanly via prebuilt wheel (`pip install mysqlclient`) — no compiler issues on this setup.

### Bug Encountered & Fixed: `SECRET_KEY` not found
**Symptom:** `django.core.exceptions.ImproperlyConfigured: Set the SECRET_KEY environment variable`

**Root cause:** `BASE_DIR` in `config/settings/base.py` was computed with `Path(__file__).resolve().parent.parent` (2 levels), but since settings now live one folder deeper (`config/settings/base.py` instead of `config/settings.py`), it needed **3** `.parent` calls to correctly reach the project root where `.env` actually lives. The old Django-generated `BASE_DIR` line had silently survived after the settings split, undoing the intended fix.

**Fix:**
```python
BASE_DIR = Path(__file__).resolve().parent.parent.parent
```

**Lesson:** Any time a file moves deeper into a folder structure, all `__file__`-relative path logic must be re-audited. This is a category of bug, not a one-off — always verify path assumptions explicitly (e.g., temporary `print()` checks) before trusting them, especially after restructuring.

### Final `DATABASES` Config (`config/settings/base.py`)
```python
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="127.0.0.1"),
        "PORT": env("DB_PORT", default="3306"),
        "OPTIONS": {"charset": "utf8mb4"},
    }
}
```

`manage.py`, `wsgi.py`, `asgi.py` updated to point to `config.settings.development` as the active settings module (hardcoded for now; production will override via Render's environment config).

### Verification
`python manage.py migrate` succeeded — created all Django built-in tables (`auth_user`, `django_admin_log`, `django_session`, etc.), confirmed via `SHOW TABLES;` in MySQL. End-to-end Django ↔ MySQL connection verified.

### Git Hygiene Check
Before committing, verified via `git status --ignored`:
- **Tracked:** `.env.example`, `.gitignore`, `config/`, `manage.py`, `requirements/`
- **Ignored (correctly excluded):** `.env`, `__pycache__/`, `venv/`

Confirmed via `git show --stat HEAD` that the actual commit contained no secrets. Repository was connected to a GitHub remote (via VS Code GUI) — verified clean before and after push.

**Milestone 2 commit:**
```
feat: configure Django project with split settings and MySQL connection
```

---

## Milestone 3: Database Design

### Entities
Category, Product, ProductImage, Inquiry, ActivityLog, plus Django's built-in `User` model (used directly for AdminUser — no custom model needed yet).

### Relationship Decisions

| Relationship | Type | `on_delete` | Reasoning |
|---|---|---|---|
| Category → Product | One-to-many | `PROTECT` | Mandatory FK; prevents accidental data loss — admin must reassign/archive products before deleting a category |
| Product → ProductImage | One-to-many | `CASCADE` | Images are meaningless without their parent product; safe since Products are never hard-deleted anyway |
| Product → Inquiry | One-to-many | `PROTECT` | Inquiries are historical customer records; blocks hard-delete of a product with inquiry history as a safety net (doesn't block status changes/archiving, since that's just an UPDATE, not a DELETE) |
| ActivityLog → (any model) | Generic | n/a (`ContentType` framework) | Built using Django's `ContentType` + `GenericForeignKey` (`content_type` + `object_id`) so logs can reference Product, Category, or any future model — trades DB-level referential integrity for flexibility, acceptable for an audit log |

### Key Design Catch: Category vs. Fabric Conflation
The original SRS listed "Silk," "Cotton," "Georgette," "Chiffon" under **Categories** alongside "Banarasi," "Bridal," "Party Wear" — but these represent two different classification axes: **style/occasion** (Category) vs. **fabric material** (Fabric). A saree can be e.g. Category="Banarasi" + Fabric="Silk" simultaneously. Resolved by treating Fabric as a separate field, not folded into Category.

**Decision:** Fabric and Color are kept as `CharField` with Django `choices=` (a fixed Python list) rather than separate lookup tables — simpler schema, fewer joins, but still enforces a controlled vocabulary (avoids inconsistent free-text entries like "Silk" vs "silk " vs "Pure Silk") since both are searchable/filterable per the SRS.

### Normalization Pass
- 1NF/2NF/3NF check passed for all entities — no repeating groups, no partial/transitive dependencies.
- `slug` fields added to **Category** and **Product** (unique, SEO-friendly URLs) — added now since backfilling slugs onto existing data later requires a migration script, more friction than adding upfront.

### Indexing Strategy
Mapped directly to SRS-required search/filter fields:

| Field | Index Type | Reasoning |
|---|---|---|
| `product_code` | Unique (auto) | Business-unique identifier |
| `category` (FK) | Auto-indexed | Django indexes FKs automatically |
| `name` | Indexed | Frequently searched |
| `status` | Indexed | Most-run query: filter to Published/non-archived |
| `fabric`, `color` | Indexed | Low-cardinality, frequently filtered |
| `price` | Indexed | Range queries (price filters) |
| `is_featured` | Indexed | Homepage "Featured" section query |

**Trade-off noted:** indexes speed up reads but slightly slow writes and use disk space. Justified here because this app is read-heavy (customers browsing) and write-light (occasional admin edits) — being generous with indexes is appropriate for this specific usage pattern, not a universal rule.

### Final Schema

```
Category
├── id (PK)
├── name
├── slug (unique)
└── created_at

Product
├── id (PK)
├── category_id (FK → Category, PROTECT, mandatory, auto-indexed)
├── product_code (unique, indexed)
├── name (indexed)
├── slug (unique)
├── description
├── price (indexed)
├── discount_price (nullable)
├── quantity
├── fabric (choices, indexed)
├── color (choices, indexed)
├── status (choices: draft/published/sold_out/hidden/archived, indexed)
├── is_featured (indexed)
├── created_at
└── updated_at

ProductImage
├── id (PK)
├── product_id (FK → Product, CASCADE, auto-indexed)
├── image
├── is_primary
└── uploaded_at

Inquiry
├── id (PK)
├── product_id (FK → Product, PROTECT, auto-indexed)
├── message
└── created_at

ActivityLog
├── id (PK)
├── content_type_id (FK → ContentType)
├── object_id
├── action
├── description
├── performed_by (FK → User, nullable, SET_NULL)
└── timestamp
```

---

## Next: Milestone 4 — Django Models
Translate the schema above into actual `models.py` files across `catalog`, `inquiries`, and `activity_log` apps — field types, `Meta` classes, indexes, `__str__` methods, and slug auto-generation logic.