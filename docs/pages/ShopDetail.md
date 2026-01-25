# Shop detail

**File:** `ShopDetail.tsx`  
**Route:** `/shops/:shopId`  
**Auth:** Required

---

## Goals

1. **Shop info** — Name, platform, connection status.
2. **Products/listings** — List products or listings for this shop; link to Products/Listings.
3. **Actions** — Sync, disconnect.

**User goal:** Inspect one shop and manage its products/listings.

---

## UI design

- **Header:** Shop name, platform badge, “Sync”, “Disconnect”.
- **Content:** Products/listings table or cards; “View in Listings” / “Compare” links where relevant.

### Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| SD1 | Shop detail loads for valid `shopId` | Shop name and platform visible. |
| SD2 | Invalid `shopId` handled | 404 or error message; no crash. |
| SD3 | “Sync” triggers sync | Loading then refresh. |
| SD4 | Links to Comparison work | e.g. “Compare” → `/comparison?product=...`. |
| SD5 | Theme applied | Page uses theme variables. |
