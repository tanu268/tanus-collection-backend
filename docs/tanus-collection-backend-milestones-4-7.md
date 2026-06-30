# Tanu's Collection — Backend Development Log (Part 2)

**Continues from:** `tanus-collection-backend-milestones-1-3.md`
**Covers:** Milestone 4 (Django Models) → Milestone 7 (API Design)

---

## Milestone 4: Django Models

### Apps Created
```
apps/core/          ← abstract base model (TimeStampedModel)
apps/catalog/        ← Category, Product, ProductImage
apps/inquiries/       ← Inquiry
apps/activity_log/    ← ActivityLog
```

Registered in `INSTALLED_APPS` as `apps.core`, `apps.catalog`, `apps.inquiries`, `apps.activity_log`. Each app's `apps.py` `name` field had to be corrected to the full dotted path (e.g. `name = "apps.catalog"`, not `"catalog"`) since the apps live inside an `apps/` container folder rather than at the project root.

**Real bug hit and fixed:** copy-paste error left two different `apps.py` files both declaring `name = "apps.catalog"` (one in `catalog/`, a stray copy in `activity_log/`), causing `ImproperlyConfigured: Application labels aren't unique`. Fixed by ensuring each app's `apps.py` declares its own correct `name`.

### `apps/core/models.py` — Abstract base
```python
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```
- `abstract = True` → no separate DB table; fields copied directly into subclasses (avoids unnecessary multi-table-inheritance joins).
- `auto_now_add` → set once, at creation only. `auto_now` → updated on every save. Mixing these up silently corrupts "created" vs "updated" semantics — a classic, hard-to-notice bug since nothing errors, the data is just quietly wrong.

### `apps/catalog/models.py` — Category, Product, ProductImage

**Category**
- `name` (unique), `slug` (unique, auto-generated via `slugify()` in `save()`, only if blank — so renaming a category later doesn't silently break existing URLs).
- `verbose_name_plural = "Categories"` to fix Django's naive "Categorys" pluralization.

**Product**
- `Status`, `Fabric`, `Color` implemented as nested `models.TextChoices` classes (modern Django idiom — gives referenceable constants like `Product.Status.SOLD_OUT`, avoids typo-prone raw strings).
- **Key catch from Milestone 3 resolved in code:** original SRS conflated Category (occasion/style: Banarasi, Bridal) with Fabric (material: Silk, Cotton) — kept as separate fields.
- `color` and `border_color` both added — a real domain detail the SRS missed (sarees commonly have a main color + a separate border/accent color). `border_color` reuses the same `Color` choices, is nullable (genuinely optional, not just deferred).
- `discount_price`: `null=True, blank=True` together — a real optional value, contrasted against `slug`'s `blank=True` only (slug is never actually empty in the DB, just auto-filled before save).
- `quantity`: `PositiveIntegerField` — rejects negative stock at the validation level.
- Indexes (`db_index=True`) applied to `product_code`, `name`, `price`, `fabric`, `color`, `status`, `is_featured` — matches the indexing strategy from Milestone 3, justified by this app's read-heavy/write-light usage pattern.
- `category` FK: `on_delete=PROTECT` — blocks deleting a Category that still has products.
- Slug auto-generated from `name + product_code` (guarantees uniqueness without a collision-suffix hack).
- `objects = ProductQuerySet.as_manager()` — custom queryset with `.public()` method (filters `status=PUBLISHED`), giving one single source of truth for "what's customer-visible," reusable everywhere instead of re-writing the filter in every view/serializer.

**ProductImage**
- `product` FK: `on_delete=CASCADE` (images are meaningless without their parent product; safe since Products are never hard-deleted).
- `upload_to="products/%Y/%m/"` — date-partitioned storage folders, avoids one giant flat folder once the catalog scales.
- `is_primary` boolean — no DB-level uniqueness constraint enforcing "only one primary per product" (MySQL's partial/conditional unique constraints are limited); this is deliberately deferred to the service layer (Milestone 6+) rather than the database.
- `Meta.ordering = ["-is_primary", "created_at"]` — primary image always returned first from any query, no extra logic needed in views/serializers.

### `apps/inquiries/models.py` — Inquiry
- `product` FK: `on_delete=PROTECT` — blocks hard-deleting a Product with inquiry history (a safety net; doesn't block status-based archiving, since that's an UPDATE not a DELETE).
- First cross-app import in the project (`from apps.catalog.models import Product`) — established a one-way dependency direction (`inquiries` depends on `catalog`, never the reverse) to avoid circular imports.

### `apps/activity_log/models.py` — ActivityLog (generic, via ContentType)
- `content_type` (FK to `ContentType`) + `object_id` (`PositiveIntegerField`) + `content_object` (`GenericForeignKey`) — lets one log table reference rows in *any* model (Product today, Category or others later), trading DB-level referential integrity for flexibility (acceptable for an audit log).
- `performed_by`: FK to `settings.AUTH_USER_MODEL` (not a hardcoded `User` import — future-proofs against ever swapping the user model), `on_delete=SET_NULL` — deleting an admin account never erases their historical log entries.
- Composite index on `["content_type", "object_id"]` — matches the real query pattern ("all logs for Product #47") far more efficiently than two separate single-column indexes.

### Migrations
All three new apps' `makemigrations` output reviewed manually before applying — confirmed correct `on_delete` behaviors, correct indexes, correct auto-detected dependency on `contenttypes` and `swappable_dependency(settings.AUTH_USER_MODEL)`. `migrate` applied successfully; new tables (`catalog_category`, `catalog_product`, `catalog_productimage`, `inquiries_inquiry`, `activity_log_activitylog`) confirmed created.

---

## Milestone 5: Django Admin

Goal: admin usable by a real, non-technical business owner — not just a developer tool.

### Category & Product registration
- `list_display`, `search_fields`, `list_filter` configured to match SRS search/filter requirements directly (search by Name/Product Code; filter by Status, Category, Fabric, Color, Featured).
- **`ProductImageInline`** (`TabularInline`) — lets the admin upload/manage a product's images directly on the Product edit page, instead of a separate disconnected screen.
- **Image preview** added via a custom `ModelAdmin` method (`image_preview`) using `django.utils.html.format_html` — never hand-built HTML with f-strings/`.format()`, since that risks XSS; `format_html` auto-escapes inserted values safely.
- **Real bug caught and fixed:** an early duplicate `class ProductImageInline` definition (old simple version + new version with preview) left dead/confusing code in the same file — same category of mistake as the `apps.py` duplication. Lesson: when replacing a class with an updated version, the old one must be deleted, not left alongside.

### Inquiry & ActivityLog registration
- **Inquiry**: `readonly_fields` on all fields — admin can view customer inquiries but not edit the customer's original message/product reference. `search_fields` uses `product__name` / `product__product_code` (double-underscore = relationship traversal in Django's ORM).
- **ActivityLog**: `has_add_permission` and `has_delete_permission` overridden to return `False` — makes this model **view-only** in the admin. Rationale: an audit trail that can be manually edited or deleted by the people it's auditing isn't trustworthy. Entries can only ever be created programmatically (signals/services), never by a human clicking "Add."

### Bulk actions
- `mark_as_hidden` / `mark_as_published` actions added to `ProductAdmin`.
- **Important architectural tension surfaced:** Django's `queryset.update()` is a fast, single SQL statement but completely bypasses each instance's `.save()` method — meaning any logic living in `save()` (or signals tied to `post_save`) is silently skipped during bulk actions. Flagged here, fully resolved in Milestone 6.

---

## Milestone 6: Business Logic

Central question for every rule: **does this belong in the model's `save()`, a signal, or a service function — and why?**

### Rule 1 — Quantity reaching zero → auto "Sold Out"; restocking reverts to "Published"
Implemented as a standalone service function, not a model method:

```python
# apps/catalog/services.py
def sync_status_with_quantity(product: Product) -> None:
    if product.quantity == 0 and product.status != Product.Status.SOLD_OUT:
        product.status = Product.Status.SOLD_OUT
    elif product.quantity > 0 and product.status == Product.Status.SOLD_OUT:
        product.status = Product.Status.PUBLISHED
```
Called explicitly inside `Product.save()`. Kept as a separate function (Service Layer pattern) rather than a model method so callers control *when* to act on the result, and so the rule isn't locked to firing only on save.

**Local import inside `save()`** (`from .services import sync_status_with_quantity`) — deliberate, not sloppy: avoids a circular import, since `services.py` itself imports `Product` from `models.py` at module level. Delaying the import until the function actually runs breaks the cycle.

**Scope decision confirmed:** only reverts `SOLD_OUT → PUBLISHED` specifically — a `Hidden` or `Draft` product that happens to hit zero quantity and gets restocked stays `Hidden`/`Draft`, untouched. Narrow, safe default.

**Verified live:** setting quantity to 0 on a real product correctly auto-flipped status to `sold_out` in MySQL.

### Rule 2 — Hidden/Draft/Archived products excluded from public queries
Implemented as a custom `QuerySet`/`Manager` method rather than scattered `.filter()` calls:
```python
class ProductQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status=Product.Status.PUBLISHED)
```
Single inclusion check (only `PUBLISHED` is visible) rather than a list of exclusions — simpler and harder to get wrong. Will be exercised once real API views exist (Milestone 8).

### Rule 3 — Every meaningful change logged to ActivityLog
Generic logging service:
```python
# apps/activity_log/services.py
def log_activity(instance, action, description="", performed_by=None):
    ActivityLog.objects.create(
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        action=action,
        description=description,
        performed_by=performed_by,
    )
```
Triggered via a `post_save` signal (not `save()` itself) — logging is a side effect/cross-cutting concern, not part of what a Product fundamentally *is*, so it belongs in a signal rather than bloating the model's own save logic.

```python
# apps/catalog/signals.py
@receiver(post_save, sender=Product)
def log_product_save(sender, instance, created, **kwargs):
    if created:
        log_activity(instance, action="created", description=f"Product '{instance.name}' added to catalog.")
    else:
        log_activity(instance, action="updated", description=f"Product '{instance.name}' was updated.")
```
Connected via `CatalogConfig.ready()` in `apps/catalog/apps.py` (signals must be explicitly imported at app-ready time, not auto-discovered).

**Real bug hit and fixed:** the `ready()` method was initially added to the wrong file (`apps/activity_log/apps.py` instead of `apps/catalog/apps.py`), reintroducing the duplicate-app-label error from Milestone 4. Fixed by moving the method to the correct file and restoring `activity_log`'s own correct config.

**Known, accepted limitation for V1:** `post_save` only reveals *that* a save happened, not *which fields changed*. Logs record "what happened" and "to what" (created/updated + product name), not a full field-level diff. True before/after change tracking would need `pre_save` comparison or a package like `django-simple-history` — explicitly deferred as out of scope for now, not an oversight.

**Verified live (full chain):** admin create → log row with `action='created'`; admin edit (quantity → 0) → status auto-changed to `sold_out` *and* a second log row (`action='updated'`) appeared in the same save — confirming Rule 1 and Rule 3 work together correctly in one save cycle.

### Bulk-action / signal gap — identified and fixed
`ProductAdmin`'s bulk actions originally used `queryset.update(status=...)`, which (as flagged in Milestone 5) bypasses `.save()` entirely — meaning bulk-hidden/published products were **not** being logged. Fixed by switching to an explicit loop:
```python
for product in queryset:
    product.status = Product.Status.HIDDEN
    product.save()
    count += 1
```
**Trade-off named explicitly:** this is slower than one bulk SQL `UPDATE` (one DB round-trip per item instead of one for all), but correctness (every change logged, every business rule re-applied) is worth it at this business's actual scale (hundreds of products, not millions). Flagged as a deliberate, scale-appropriate choice, not a universal rule.

**Verified live:** selected 2 products, ran "Mark as Hidden" bulk action — both products' status changed, and **both** received individual ActivityLog entries, confirming the fix works correctly across multiple items at once.

---

## Milestone 7: API Design

Designed on paper before any DRF code — same discipline as the Milestone 3 database design phase. Triggered in part by reviewing an existing frontend scaffold (Lovable-generated, TanStack Start/React) that had several contract mismatches against our actual backend model — resolving those mismatches became part of this design pass.

### Public vs. Admin endpoint split
Two distinct audiences with different needs, kept as genuinely separate endpoint sets (not one set with conditional permission checks), because the *response shape* differs too — not just access control.

**Public (read-mostly, no auth):**
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/products/` | List published products, filterable |
| GET | `/api/products/<slug>/` | Single product detail |
| GET | `/api/categories/` | List categories |
| GET | `/api/categories/<slug>/` | Single category + its products |
| POST | `/api/inquiries/` | Customer submits a WhatsApp inquiry |

**Admin (authenticated, full CRUD):**
| Method | Endpoint | Purpose |
|---|---|---|
| GET/POST | `/api/admin/products/` | List (any status) / create |
| GET/PUT/PATCH/DELETE | `/api/admin/products/<id>/` | Retrieve/update/archive |
| GET/POST | `/api/admin/categories/` | List/create |
| GET/POST | `/api/admin/product-images/` | Upload images |
| GET | `/api/admin/inquiries/` | View customer inquiries |
| GET | `/api/admin/activity-log/` | View audit trail (read-only) |
| GET | `/api/admin/dashboard/` | Stats: counts by status + recent activity |

**Slugs for public URLs, IDs for admin URLs** — deliberate, not inconsistent: public URLs benefit from being meaningful/stable (SEO, matches the frontend's existing slug-based routing); admin operations act on a specific row the admin already has open, where a numeric ID is simpler and avoids any slug-uniqueness edge cases during editing.

**`DELETE /api/admin/products/<id>/` → soft archive, not real deletion.** Sets `status=ARCHIVED` and calls `.save()` (so the existing `post_save` signal still logs the action) rather than calling `.delete()`. Chosen specifically because REST conventions mean any client (including a future frontend built by someone unfamiliar with this codebase) will correctly assume `DELETE` makes the item disappear from normal views — matching that expectation while honoring the underlying no-hard-delete policy is better than inventing a non-standard verb mapping.

### Key contract decisions (resolving frontend mismatches found during review)

| Question | Decision | Reasoning |
|---|---|---|
| `price`/`discount_price` semantics | `price` = base price, `discount_price` = lower sale price (nullable) — backend stays authoritative | Avoids changing backend model; frontend mock types will be updated later to match, not the reverse |
| `colorHex` per color | Not added to backend | Purely cosmetic/UI concern; frontend can maintain its own color→hex map without backend involvement |
| "is product new" badge | Computed by frontend from `created_at`, not backend | Presentation logic with no data-integrity implications; keeping it frontend-side means the "recency window" can change without any backend deploy |
| "bestseller" badge | Explicitly out of scope for V1 | No sales/order data tracked yet (WhatsApp-only inquiries); would need either a manual `is_bestseller` admin flag or an inquiry-count proxy later |
| Exposing `quantity` to public API | **Not exposed** in public responses | Information-hiding decision — exact stock counts have no customer benefit and could leak competitively sensitive inventory data; admin-only serializer will include it |

### Response shapes

**Detail — `GET /api/products/<slug>/`:**
```json
{
  "id": 1,
  "slug": "banarasi-silk-saree-tc-0001",
  "product_code": "TC-0001",
  "name": "Banarasi Silk Saree",
  "category": { "id": 3, "name": "Banarasi", "slug": "banarasi" },
  "description": "...",
  "price": "18900.00",
  "discount_price": null,
  "fabric": "silk",
  "fabric_display": "Silk",
  "color": "red",
  "color_display": "Red",
  "border_color": "gold",
  "border_color_display": "Gold",
  "status": "published",
  "is_featured": true,
  "is_available": true,
  "images": [
    { "url": "/media/products/2026/06/img1.jpg", "is_primary": true },
    { "url": "/media/products/2026/06/img2.jpg", "is_primary": false }
  ],
  "created_at": "2026-06-29T12:09:24Z"
}
```
- `category` nested (not just an ID) — avoids the frontend needing a second request just to resolve a category name; trade-off is a slightly larger payload for far fewer round-trips.
- `*_display` fields (e.g. `fabric_display`) ship alongside raw choice values — raw value for programmatic use, human-readable label for direct display; comes for free from Django's `TextChoices`.
- `is_available` is a **computed** field (not a real DB column), derived from `status`.

**List — `GET /api/products/`:**
```json
{
  "count": 42,
  "next": "/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "slug": "banarasi-silk-saree-tc-0001",
      "name": "Banarasi Silk Saree",
      "category": { "id": 3, "name": "Banarasi", "slug": "banarasi" },
      "price": "18900.00",
      "discount_price": null,
      "color": "red",
      "color_display": "Red",
      "is_featured": true,
      "thumbnail": "/media/products/2026/06/img1.jpg",
      "created_at": "2026-06-29T12:09:24Z"
    }
  ]
}
```
Deliberately leaner than the detail response (no `description`, no full `images` array, no `fabric`/`border_color`) — a paginated grid of 20+ cards only needs enough to render a card, not the full product page's worth of data. `thumbnail` flattens the primary image to a single URL string.

Standard DRF `PageNumberPagination` shape (`count`/`next`/`previous`/`results`) — included from day one rather than retrofitted later, since an unpaginated endpoint returning the full catalog gets progressively worse as inventory grows.

### Query parameters (`GET /api/products/?...`)
| Param | Behavior |
|---|---|
| `category=<slug>` | filter by category |
| `fabric=<value>` | filter by fabric |
| `color=<value>` | filter by color |
| `min_price` / `max_price` | price range |
| `featured=true` | featured only |
| `search=<text>` | matches SRS's name/product-code search requirement |
| `ordering=<field>` or `-<field>` | sort control |

### `POST /api/inquiries/`
**Request:** `{ "product": 1, "message": "..." }`
**Response (201):** `{ "id": 14, "product": 1, "message": "...", "created_at": "..." }`

Flagged for Milestone 8: this is a public, unauthenticated POST endpoint — needs DRF throttling/rate-limiting to prevent spam, deliberately deferred to implementation rather than solved at design time.

### `GET /api/admin/dashboard/`
```json
{
  "total_products": 42,
  "available_products": 30,
  "sold_out_products": 5,
  "hidden_products": 4,
  "draft_products": 2,
  "archived_products": 1,
  "featured_products": 8,
  "recent_activity": [
    { "action": "updated", "description": "...", "created_at": "..." }
  ]
}
```
Resolves the SRS's "Dashboard Statistics" requirement that was explicitly deferred back in Milestone 5 — now has a designed home: simple `.count()` aggregates per status plus the 5 most recent `ActivityLog` entries.

---

## Frontend Review Notes (reference, not a milestone)

An existing frontend scaffold (`artful-brand-sculptor-main` — TanStack Start/React 19, Lovable-generated) was reviewed against the backend schema. Structure (routes for shop/product/category/inquiry/admin sections) closely mirrors the SRS. Key mismatches identified and resolved via the API design decisions above:
- `Category` type conflated occasion/style with fabric (same issue caught in Milestone 3) — frontend types will need updating once real API integration begins.
- `stock` vs `quantity` — naming only, resolved at the serializer level.
- `price`/`originalPrice` inverted semantics vs. backend's `price`/`discount_price` — resolved in favor of backend semantics (see decisions table above).
- `colorHex`, `badges` (new/featured/bestseller) — resolved per decisions table above.
- `images: string[]` flat array — backend will flatten `ProductImage` into ordered URLs (primary first) in the serializer.

`src/services/products.ts` is currently mock-only (`setTimeout`-simulated), explicitly designed to be swapped for real API calls later — no premature integration attempted; deferred until Milestone 8 endpoints actually exist.

---

## Next: Milestone 8 — REST APIs
Implement the actual DRF serializers (public vs. admin, list vs. detail), viewsets/views, URL routing, filtering (`django-filter`), pagination, and permissions — building exactly to the contract designed in Milestone 7, including the public/admin response-shape split, the DELETE-as-archive override, and inquiry endpoint throttling.