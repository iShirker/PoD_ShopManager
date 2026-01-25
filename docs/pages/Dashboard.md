# Dashboard

**File:** `Dashboard.tsx`  
**Route:** `/`  
**Auth:** Required

---

## Goals

1. **Unified overview** — Single place to see all connected Etsy/Shopify shops and PoD suppliers.
2. **Quick KPIs** — Revenue, orders, listings (per shop and combined); at-a-glance health.
3. **Quick actions** — Shortcuts to Compare Prices, View Products, Create Template, Connect shops/suppliers.
4. **Onboarding** — Clear CTAs when no shops or suppliers are connected.

**User goal:** Understand “how is my business doing?” and jump into high-value tasks without hunting through the app.

---

## Feature research

- **Etsy Shop Stats** — Sellers track views, visits, orders, conversion; focus on long-term trends, not daily noise.
- **Shopify KPIs** — Revenue, orders, conversion, AOV; 70+ KPIs, dashboards by sales/marketing/operations.
- **Multi-store** — Sellers want one dashboard across Etsy + Shopify; revenue diversification and channel comparison.
- **PoD** — Connect-before-use: dashboard should prompt to connect shops/suppliers when missing.

---

## UI design

### Layout

- **Header:** “Dashboard” title, optional period selector (7d / 30d / 90d) if we show period-based KPIs.
- **Connected strip (optional):** Compact list of connected shops (Etsy/Shopify) and suppliers (Gelato, Printify, Printful) with status indicators.
- **KPI cards:** 2×2 or 1×4 grid:
  - Revenue (total or period)
  - Orders (total or period)
  - Listings count
  - Products count (My Products)
- **Quick actions:** 3 cards (or buttons):
  - Compare Prices → `/comparison`
  - View Products → `/products`
  - Create Template → `/templates`
- **Connect CTAs:** When no shops: “Connect Etsy” / “Connect Shopify”. When no suppliers: “Connect Gelato” / “Connect Printify” / “Connect Printful”. Use modals (ShopLoginModal, SupplierLoginModal) or links to `/shops`, `/suppliers`.
- **Footer:** Optional “Recent orders” or “Low stock” teaser with link to Orders / Products.

### Key elements

- Page title: “Dashboard”.
- KPI cards with icons (DollarSign, ShoppingCart, List, Package).
- Quick-action cards: icon, title, short description, link.
- Connect buttons with platform/supplier icons.

### Actions

- Click “Compare Prices” → navigate to `/comparison`.
- Click “View Products” → navigate to `/products`.
- Click “Create Template” → navigate to `/templates`.
- Click “Connect Etsy” / “Connect Shopify” → open ShopLoginModal or redirect to connect flow.
- Click “Connect Gelato” / “Connect Printify” / “Connect Printful” → open SupplierLoginModal or redirect.

### Accessibility

- Semantic headings (h1, h2).
- Focus order: title → KPIs → quick actions → connect CTAs.
- Sufficient colour contrast (theme-aware).

---

## Functional tests

| ID | Description | Pass condition |
|----|-------------|----------------|
| D1 | Dashboard loads when authenticated user visits `/` | Page renders; “Dashboard” visible. |
| D2 | Unauthenticated user visiting `/` is redirected to `/login` | Redirect to `/login`. |
| D3 | KPI cards display | At least Revenue, Orders, Listings (or placeholders) visible. |
| D4 | “Compare Prices” quick action navigates to `/comparison` | Click → URL is `/comparison`. |
| D5 | “View Products” quick action navigates to `/products` | Click → URL is `/products`. |
| D6 | “Create Template” quick action navigates to `/templates` | Click → URL is `/templates`. |
| D7 | Connect shop CTA present when no shops | “Connect Etsy” or “Connect Shopify” (or both) visible. |
| D8 | Connect supplier CTA present when no suppliers | At least one “Connect Printify” / “Connect Printful” / “Connect Gelato” visible. |
| D9 | Connect Etsy opens shop connect flow | Click Connect Etsy → modal or connect flow; no JS error. |
| D10 | Connect supplier opens supplier connect flow | Click Connect Printify (or other) → modal or connect flow; no JS error. |
| D11 | Theme applied | Dashboard uses theme variables (no hardcoded colours that ignore theme). |
