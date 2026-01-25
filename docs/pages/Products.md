# My Products

**File:** `Products.tsx`  
**Route:** `/products`  
**Auth:** Required

---

## Goals

1. **List user’s products** — Products added from catalog; show title, SKU, supplier, variants.
2. **Search/filter** — By name, supplier, product type.
3. **Add from catalog** — Link or button to Catalog; add flow.
4. **Actions** — View, compare, delete; link to listings.

**User goal:** Central list of “my products”; add, search, compare, manage.

---

## Feature research

- **PoD product management** — Sellers need SKU tracking, variant (size/color) clarity, supplier per product.
- **Add from catalog** — Browse supplier catalog → add to “my products” is standard flow.

---

## UI design

- **Header:** “My Products”; “Add from catalog” button; search input.
- **Table or cards:** Title, SKU, supplier, variants; “Compare”, “Delete”, link to listing.
- **Pagination** if many products.
- **Empty state:** “No products” + “Add from catalog”.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| P1 | Products page loads at `/products` | “My Products” / “Products” title; list or empty state. |
| P2 | Products listed with key fields | Title, SKU or supplier visible. |
| P3 | “Add from catalog” navigates to `/products/catalog` | URL is `/products/catalog`. |
| P4 | Search filters list | Typing updates visible products. |
| P5 | “Compare” links to `/comparison` | URL includes `product` or `user_product` param. |
| P6 | “Delete” removes product (with confirm) | List updates after confirm. |
| P7 | Theme applied | Page uses theme variables. |
