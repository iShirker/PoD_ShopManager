# Mockup Studio

**File:** `Mockups.tsx`  
**Route:** `/mockups`  
**Auth:** Required

---

## Goals

1. **Create preview mockups** — Pick product, upload design, place on product template.
2. **Generate image** — Preview and optionally export (PNG/print-ready).
3. **Optional:** Bulk mockups, link to listing.

**User goal:** Create listing-ready mockups without leaving the app.

---

## Feature research

- **PoD mockup tools:** Printify, Printful, Mockey, Dynamic Mockups — upload design, pick product/color, generate image.
- **UX:** Product picker → design upload → placement → generate → download.

---

## UI design

- **Header:** “Mockup Studio”.
- **Product selector** — Choose product (from catalog or template).
- **Design upload** — File input; optional placement/size.
- **Preview** — Generated mockup image; “Download” or “Use in listing”.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| M1 | Mockup Studio page loads at `/mockups` | “Mockup Studio” title; product picker or upload visible. |
| M2 | Selecting product and uploading design shows preview | Preview image displayed. |
| M3 | “Download” exports image | File download or blob. |
| M4 | Theme applied | Page uses theme variables. |
