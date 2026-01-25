# Discounts

**File:** `Discounts.tsx`  
**Route:** `/discounts`  
**Auth:** Required

---

## Goals

1. **List discount programs** — Name, type (%, fixed), value, active/inactive.
2. **Create / edit / delete** — CRUD for programs.
3. **Optional:** Schedule, margin check, sync to Etsy/Shopify (when implemented).

**User goal:** Manage sales and promos; create and schedule discounts.

---

## UI design

- **Header:** “Discounts” or “Discount Programs”; “Create” button.
- **List** of programs: name, type, value, active; edit, delete.
- **Form** for create/edit.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| D1 | Discounts page loads at `/discounts` | “Discounts” title; list or empty state. |
| D2 | Programs listed | Name, type, value, active state. |
| D3 | Create program opens form | Form visible; submit creates. |
| D4 | Delete removes program | List updates. |
| D5 | Theme applied | Page uses theme variables. |
