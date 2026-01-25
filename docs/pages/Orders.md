# Orders

**File:** `Orders.tsx`  
**Route:** `/orders`  
**Auth:** Required

---

## Goals

1. **List orders** — From Etsy & Shopify; order ID, platform, customer, total, status.
2. **Filter** — Platform, shop, status; pagination.
3. **Order detail** — Click to view items, customer, fulfillment; link to Fulfillment.

**User goal:** View and search orders; open detail.

---

## UI design

- **Header:** “Orders”; filters; optional search.
- **Table:** Order, platform, customer, total, status; link to detail.
- **Pagination.**
- **Empty state** when no orders.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| O1 | Orders page loads at `/orders` | “Orders” title; table or empty state. |
| O2 | Orders shown with key columns | Order ID, platform, total, status. |
| O3 | Filter by platform updates list | Results update. |
| O4 | Pagination works | Next/prev updates list. |
| O5 | Click order opens detail or navigates | Detail view or `/orders/:id` if implemented. |
| O6 | Theme applied | Page uses theme variables. |
