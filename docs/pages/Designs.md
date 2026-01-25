# Designs

**File:** `Designs.tsx`  
**Route:** `/designs`  
**Auth:** Required

---

## Goals

1. **Design library** — Upload, store, tag designs; thumbnails.
2. **Search/organize** — By name, tags.
3. **Use in mockups/listings** — Link to Mockup Studio or product.

**User goal:** Central design library; reuse designs across products.

---

## UI design

- **Header:** “Designs”; “Upload” button.
- **Grid** of design thumbnails; name, tags; actions (use, delete).

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| DS1 | Designs page loads at `/designs` | “Designs” title; grid or empty state. |
| DS2 | Upload adds design | New thumbnail in grid. |
| DS3 | Theme applied | Page uses theme variables. |
