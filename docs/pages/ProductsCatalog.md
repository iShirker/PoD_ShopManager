# Catalog

**File:** `ProductsCatalog.tsx`  
**Route:** `/products/catalog`  
**Auth:** Required

---

## Goals

1. **Browse supplier catalog** — By connection (Gelato, Printify, Printful); search, filter.
2. **Add to My Products** — “Add” per product; feedback on success/failure.
3. **Pagination** — Handle large catalogs.

**User goal:** Find supplier products and add them to “My Products”.

---

## UI design

- **Header:** “Catalog”; connection/supplier selector; search.
- **Grid or list** of catalog items: image, title, brand/model, “Add” button.
- **Pagination** or “Load more”.
- **Empty state** when no connection or no results.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| PC1 | Catalog page loads at `/products/catalog` | “Catalog” title; selector or list. |
| PC2 | Catalog items shown for selected connection | Products from supplier visible. |
| PC3 | “Add” adds product to My Products | Success feedback; product addable or already-added state. |
| PC4 | Search filters catalog | Results update. |
| PC5 | Theme applied | Page uses theme variables. |
