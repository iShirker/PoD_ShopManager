# SEO Assistant

**File:** `ListingsSeo.tsx`  
**Route:** `/listings/seo`  
**Auth:** Required

---

## Goals

1. **Title optimization** — Suggest or edit title; use full length (Etsy 140 chars); keyword-focused.
2. **Tags** — Suggest 13 tags; competition/search volume if available.
3. **Description** — Template or suggestions; relevant keywords.

**User goal:** Improve discoverability; optimize titles, tags, descriptions for Etsy/Shopify.

---

## Feature research

- **Etsy SEO:** Title carries most weight; 13 tags; quality images, 200+ word descriptions.
- **Tools:** EtsyCheck, Etsy Scope, RankHero offer tag generators, keyword research, listing graders.

---

## UI design

- **Header:** “SEO Assistant”.
- **Input:** Listing URL or paste title/tags/description.
- **Output:** Optimized title, tag suggestions, description tips; “Copy” or “Apply to listing”.
- **Optional:** Keyword search, competition scores.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| LSE1 | SEO Assistant page loads at `/listings/seo` | “SEO Assistant” title; input or form visible. |
| LSE2 | Entering keyword or title yields suggestions | Suggestions (tags/title) displayed. |
| LSE3 | “Copy” or “Apply” works | Copy to clipboard or navigates to listing. |
| LSE4 | Theme applied | Page uses theme variables. |
