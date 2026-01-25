# Profitability reports

**File:** `AnalyticsProfitability.tsx`  
**Route:** `/analytics/profitability`  
**Auth:** Required

---

## Goals

1. **Profitability by product/category/period** — Cost, fees, profit, margin %.
2. **Trends** — Over time when data available.

**User goal:** Understand true profitability.

---

## UI design

- **Header:** “Profitability Reports”; period/category filters.
- **Table or charts** — By product, category; profit, margin.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| APr1 | Profitability page loads at `/analytics/profitability` | “Profitability” title; table or empty state. |
| APr2 | Theme applied | Page uses theme variables. |
