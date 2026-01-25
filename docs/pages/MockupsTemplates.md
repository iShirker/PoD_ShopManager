# Customization templates

**File:** `MockupsTemplates.tsx`  
**Route:** `/mockups/templates`  
**Auth:** Required

---

## Goals

1. **Placement templates** — Product × placement (front, back, etc.); dimensions, safe zones.
2. **CRUD** — Create, edit, delete; reuse in Mockup Studio.

**User goal:** Define reusable placement rules; consistent mockups across products.

---

## UI design

- **Header:** “Customization Templates”.
- **List** of templates; create, edit, delete.
- **Form** for create/edit.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| MT1 | Customization Templates page loads at `/mockups/templates` | “Customization Templates” title; list or empty state. |
| MT2 | Create template opens form | Form visible; submit creates. |
| MT3 | Theme applied | Page uses theme variables. |
