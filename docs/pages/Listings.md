# Listings

**File:** `Listings.tsx`  
**Route:** `/listings`  
**Auth:** Required

---

## Goals

1. **List Etsy & Shopify listings** — Unified list; title, shop, SKU, price, status.
2. **Filter** — By shop, search.
3. **Pagination** — Handle many listings.

**User goal:** See all listings across shops; find and manage.

---

## UI design

- **Header:** “Listings”; search; shop filter.
- **Table:** Title, shop, SKU, price; optional link to edit/detail.
- **Pagination.**
- **Empty state** when no listings.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| LIS1 | Listings page loads at `/listings` | “Listings” title; table or empty state. |
| LIS2 | Listings shown with title, shop, SKU, price | Key columns present. |
| LIS3 | Search filters listings | Results update. |
| LIS4 | Shop filter filters listings | Results update. |
| LIS5 | Pagination works | Next/prev or page numbers update list. |
| LIS6 | Theme applied | Page uses theme variables. |
