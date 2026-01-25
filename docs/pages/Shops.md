# Shops

**File:** `Shops.tsx`  
**Route:** `/shops`  
**Auth:** Required

---

## Goals

1. **List connected shops** — Show all Etsy and Shopify stores the user has connected.
2. **Connect new shops** — “Connect Etsy”, “Connect Shopify” with clear flow (OAuth / shop domain).
3. **Per-shop actions** — View detail, sync, disconnect.
4. **Empty state** — When no shops, prompt to connect.

**User goal:** Manage Etsy and Shopify connections in one place; add or remove shops.

---

## Feature research

- **Multi-store** — Sellers use multiple Etsy shops and/or Shopify stores; unified management reduces context switching.
- **Connect flow** — OAuth for Etsy; Shopify typically requires shop domain (e.g. `mystore.myshopify.com`) then OAuth.

---

## UI design

### Layout

- **Header:** “Shops” title; “Connect Etsy” / “Connect Shopify” buttons.
- **List** of connected shops: card or table per shop.
  - Shop name, platform (Etsy / Shopify), status (connected / error).
  - Actions: “View” → `/shops/:id`, “Sync”, “Disconnect”.
- **Empty state:** Illustration or message + “Connect Etsy” / “Connect Shopify”.

### Key elements

- Page title; connect buttons; shop cards/rows; action buttons.

### Actions

- “Connect Etsy” → open modal or redirect to Etsy OAuth.
- “Connect Shopify” → prompt shop domain, then OAuth.
- “View” → navigate to `/shops/:shopId`.
- “Sync” → trigger sync; show loading, then refresh list.
- “Disconnect” → confirm; then disconnect and refresh.

### Accessibility

- Buttons and links keyboard-focusable; confirm dialog accessible.

---

## Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| S1 | Shops page loads at `/shops` | “Shops” title and connect buttons visible. |
| S2 | Connected shops listed | Each shop shows name, platform; “View” action available. |
| S3 | Empty state when no shops | Message + connect CTAs; no error. |
| S4 | “Connect Etsy” opens connect flow | Modal or redirect; no JS error. |
| S5 | “Connect Shopify” opens connect flow | Domain prompt then OAuth or modal; no JS error. |
| S6 | “View” navigates to shop detail | URL is `/shops/:shopId`. |
| S7 | “Sync” triggers sync | Loading state; list refreshes after sync. |
| S8 | “Disconnect” shows confirmation | Confirm dialog; disconnect only after confirm. |
| S9 | Theme applied | Page uses theme variables. |
