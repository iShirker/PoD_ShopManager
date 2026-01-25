# Compare & Switch

**File:** `Comparison.tsx`  
**Route:** `/comparison`  
**Auth:** Required

---

## Goals

1. **Compare prices** — Same product across connected suppliers; base price, shipping, total.
2. **Filter** — By shop, product type, supplier.
3. **Switch supplier** — One-click or bulk switch; update SKUs/listings.

**User goal:** Compare PoD costs and switch supplier to save money.

---

## UI design

- **Header:** “Supplier Comparison” or “Compare & Switch”; filters (shop, product type, supplier).
- **Summary cards:** Total products, products with savings, potential savings.
- **Table/grid:** Rows = products; columns = suppliers with prices; “Switch” action.
- **Bulk switch** (optional): Select multiple → choose supplier → apply.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| C1 | Comparison page loads at `/comparison` | Title; summary or table visible. |
| C2 | Products compared across suppliers | Prices per supplier shown. |
| C3 | Filters apply | Changing filters updates results. |
| C4 | “Switch” changes supplier | Success feedback; data refreshes. |
| C5 | Query `?product=` or `?user_product=` pre-selects product | Relevant product focused or filtered. |
| C6 | Theme applied | Page uses theme variables. |
