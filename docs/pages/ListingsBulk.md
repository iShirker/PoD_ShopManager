# Bulk Create (listings)

**File:** `ListingsBulk.tsx`  
**Route:** `/listings/bulk`  
**Auth:** Required

---

## Goals

1. **CSV/Excel import** — Upload file; map columns to title, description, tags, variants, images.
2. **Preview & validate** — Show preview; validation errors before publish.
3. **Bulk create** — Create listings to Etsy/Shopify; report success/failure.

**User goal:** Create many listings from a spreadsheet without manual one-by-one entry.

---

## Feature research

- **Etsy:** No native CSV upload; third-party tools (Nembol, CSV Lister, Shop Uploader) use templates, column mapping, image linking.
- **Shopify:** Built-in CSV import; sample template, required fields (e.g. Title), image URLs in CSV.
- **UX:** Download template → fill → upload → map → preview → import; clear validation and error report.

---

## UI design

### Layout

- **Header:** “Bulk Create”; short description.
- **Step 1 – Upload:** File input (CSV/Excel); “Download template” link.
- **Step 2 – Map columns:** Dropdowns to map CSV columns to title, description, tags, variants, etc.
- **Step 3 – Preview:** Table of first N rows; validation warnings.
- **Step 4 – Create:** “Create listings” button; progress; success/error report (count, errors list).

### Key elements

- File input; template link; column mapper; preview table; create button; report area.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| LB1 | Bulk Create page loads at `/listings/bulk` | “Bulk Create” title; upload or template option visible. |
| LB2 | “Download template” provides CSV template | File download or template content. |
| LB3 | Upload valid CSV shows preview or mapper | No crash; next step available. |
| LB4 | Validation errors shown for invalid data | Errors listed; create disabled or guarded. |
| LB5 | “Create” triggers bulk create | Loading state; report with success/failure count. |
| LB6 | Theme applied | Page uses theme variables. |
