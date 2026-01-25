# Product performance

**File:** `AnalyticsProducts.tsx`  
**Route:** `/analytics/products`  
**Auth:** Required

---

## Goals

1. **Per-product metrics** — Views, orders, revenue, margin (when available).
2. **Filter** — Period, shop, product type.

**User goal:** See which products perform best.

---

## UI design

- **Header:** “Product Performance”; filters.
- **Table** of products with metrics.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| AP1 | Product Performance page loads at `/analytics/products` | “Product Performance” title; table or empty state. |
| AP2 | Theme applied | Page uses theme variables. |
