# Design mappings

**File:** `DesignsMappings.tsx`  
**Route:** `/designs/mappings`  
**Auth:** Required

---

## Goals

1. **Map design → product/placement** — Which designs go on which products.
2. **CRUD** — Create, edit, delete mappings.

**User goal:** Reuse designs across products consistently.

---

## UI design

- **Header:** “Design Mappings”.
- **List** of mappings: design, product, placement; edit, delete.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| DM1 | Design Mappings page loads at `/designs/mappings` | “Design Mappings” title; list or empty state. |
| DM2 | Theme applied | Page uses theme variables. |
