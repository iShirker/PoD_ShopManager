# Price rules

**File:** `PricingRules.tsx`  
**Route:** `/pricing/rules`  
**Auth:** Required

---

## Goals

1. **List price rules** — Per product/variant; markup, margin, or min price.
2. **Create / edit / delete** — CRUD for rules.

**User goal:** Define pricing rules per product; automate margin or min price.

---

## UI design

- **Header:** “Price Rules”; “Create” button.
- **List** of rules: product, rule type, value; edit, delete.
- **Form** (modal or inline) for create/edit.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| PRR1 | Price Rules page loads at `/pricing/rules` | “Price Rules” title; list or empty state. |
| PRR2 | Rules listed | Product, rule type, value visible. |
| PRR3 | Create rule opens form | Form visible; submit creates rule. |
| PRR4 | Delete rule removes it | List updates. |
| PRR5 | Theme applied | Page uses theme variables. |
