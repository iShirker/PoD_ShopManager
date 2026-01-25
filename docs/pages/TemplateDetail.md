# Template detail

**File:** `TemplateDetail.tsx`  
**Route:** `/templates/:templateId`  
**Auth:** Required

---

## Goals

1. **Template info** — Name, description, default title/tags, platforms.
2. **Products in template** — List products; add, remove, set display order.
3. **Create listing** — “Create listing” from template → pick shop → publish.

**User goal:** Edit template; add products; create listing from template.

---

## UI design

- **Header:** Template name; “Edit”, “Create listing”, “Back to templates”.
- **Products section** — List; add product, remove, reorder.
- **Create listing flow** — Shop picker, confirm, submit.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| TD1 | Template detail loads for valid `templateId` | Template name and products visible. |
| TD2 | Invalid `templateId` handled | 404 or error; no crash. |
| TD3 | “Create listing” opens flow | Shop picker or confirm step. |
| TD4 | “Back” navigates to `/templates` | URL is `/templates`. |
| TD5 | Theme applied | Page uses theme variables. |
