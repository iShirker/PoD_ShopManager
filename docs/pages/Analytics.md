# Analytics overview

**File:** `Analytics.tsx`  
**Route:** `/analytics`  
**Auth:** Required

---

## Goals

1. **Summary KPIs** — Revenue, orders, listings, net profit; period (7d, 30d, 90d).
2. **Use real data** — From orders, listings (when synced).

**User goal:** Quick view of business performance.

---

## UI design

- **Header:** “Analytics Overview”; period selector (7d, 30d, 90d).
- **KPI cards:** Revenue, Orders, Listings, Net profit.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| A1 | Analytics page loads at `/analytics` | “Analytics” title; KPI cards visible. |
| A2 | Period selector updates data | Changing period refetches or updates KPIs. |
| A3 | Theme applied | Page uses theme variables. |
