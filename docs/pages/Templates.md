# Listing templates

**File:** `Templates.tsx`  
**Route:** `/templates`  
**Auth:** Required

---

## Goals

1. **List templates** — Name, description, target platforms; create, edit, delete.
2. **Create template** — Name, default title/description/tags, target platforms (Etsy, Shopify).
3. **Link to detail** — “View” → `/templates/:id`.

**User goal:** Manage listing templates; create listings from templates.

---

## UI design

- **Header:** “Listing Templates” or “Templates”; “Create” button.
- **List** of templates: name, platforms; view, edit, delete.
- **Create modal** — Name, description, default title, platforms.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| T1 | Templates page loads at `/templates` | “Templates” title; list or empty state. |
| T2 | Create template opens form | Form visible; submit creates template. |
| T3 | “View” navigates to `/templates/:id` | URL correct. |
| T4 | Delete removes template | List updates. |
| T5 | Theme applied | Page uses theme variables. |
