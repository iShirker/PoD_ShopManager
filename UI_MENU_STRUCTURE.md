# PoD Shop Manager – UI Menu & Navigation Structure

This document defines the **global navigation** (sidebar + routes) for all planned features. It maps menu items to product phases (MVP / Growth / Advanced) and subscription tiers where limits apply.

**Related:** [PRODUCT_PLAN.md](./PRODUCT_PLAN.md) · [FEATURE_PRIORITY.md](./FEATURE_PRIORITY.md) · [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md) · [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md)

---

## 0. Menu design rationale (same screen vs own screen)

**Principles:** Group by user workflow. Put **connection** tasks early (connect shops/suppliers before products/listings). Avoid a separate “Tools” section by placing Compare under Products and Templates under Listings.

### Same screen (tabs or sub-views on one page)

| Functions | Rationale | Current implementation |
|-----------|-----------|-------------------------|
| **Orders** + **Fulfillment** | Both are order-centric: “see all orders” vs “work the queue.” Same mental model; different filters. | Two routes (`/orders`, `/orders/fulfillment`). Can be merged later into one “Orders” page with “All” \| “Fulfillment” tabs. |
| **Calculator** + **Price rules** | Both define “how I price.” Calculator = ad‑hoc; rules = persistent. | Two routes (`/pricing`, `/pricing/rules`). Can be merged into one “Pricing” page with tabs. |
| **Analytics** Overview + **Product performance** + **Profitability** | All “how am I doing?” Different slices of the same data. | Three routes. Can be merged into one “Analytics” page with Overview \| Products \| Profitability tabs. |

**Decision:** Keep separate nav items and routes for now. Consolidation into tabbed single screens can follow later.

### Own screen (dedicated nav item + route)

| Function | Rationale |
|----------|-----------|
| **Dashboard** | Entry point; multi‑store overview. |
| **Shops** / **Suppliers** | Different entities (marketplaces vs PoD); separate connect/manage flows. |
| **My Products** / **Catalog** | Different workflows: “manage my products” vs “browse supplier catalog and add.” |
| **Compare & switch** | Product‑centric but distinct workflow (compare → switch). Own screen. |
| **Listings** | Core listing list/search; sync. |
| **Templates** | Listing templates → create listing. Placed under **Listings** (not “Tools”). |
| **Bulk create** / **SEO Assistant** | Different flows from main Listings view. |
| **Discounts** | Promo/sales workflow. |
| **Mockup Studio** / **Customization templates** | Create mockups vs define placement rules; related but separate. |
| **Designs** / **Design mappings** | Library vs mapping; separate UIs. |

### Section order

1. **Overview** — Dashboard first.
2. **Connections** — Shops, Suppliers. Users must connect before products/listings; place high.
3. **Products** — My Products, Catalog, **Compare & switch** (moved from Tools).
4. **Listings** — Listings, **Templates** (moved from Tools), Bulk create, SEO Assistant.
5. **Orders** — Orders, Fulfillment.
6. **Pricing & profitability** — Calculator, Price rules.
7. **Promotions** — Discounts (renamed from “Discount programs”).
8. **Mockups & customization** — Mockup Studio, Customization templates.
9. **Design library** — Designs, Design mappings.
10. **Analytics** — Overview, Product performance, Profitability.

**Removed:** Standalone **Tools** section. Compare → Products; Templates → Listings.

---

## 0b. Current vs planned menu

| Current (Layout) | Revised | Notes |
|------------------|---------|-------|
| Dashboard `/` | Dashboard `/` | Same |
| Shops, Suppliers (bottom) | **Connections** (Shops, Suppliers) | **Moved up** (second section) |
| Products + Catalog | **Products** (My Products, Catalog, **Compare & switch**) | Compare moved from Tools → Products |
| Listings, Bulk, SEO | **Listings** (Listings, **Templates**, Bulk, SEO) | Templates moved from Tools → Listings |
| Orders, Fulfillment | **Orders** (same) | Same |
| Pricing, Price Rules | **Pricing & profitability** (same) | Same |
| Discounts | **Promotions** (Discounts) | Section renamed |
| Mockups, Customization templates | **Mockups & customization** (same) | Section renamed |
| Designs, Mappings | **Design library** (same) | Same |
| Analytics (3 items) | **Analytics** (same) | Same |
| **Tools** (Compare, Templates) | — | **Removed**; items moved to Products / Listings |
| Profile, Billing | Same (footer) | Same |

---

## 1. Navigation Overview (revised)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  POD Manager                                                    [User ▾]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ▼ OVERVIEW                                                                 │
│     Dashboard                                    /                           │
│                                                                             │
│  ▼ CONNECTIONS                                                              │
│     Shops                                      /shops                        │
│     Suppliers                                  /suppliers                    │
│                                                                             │
│  ▼ PRODUCTS                                                                 │
│     My Products                                /products                     │
│     Catalog                                    /products/catalog             │
│     Compare & Switch                           /comparison                   │
│                                                                             │
│  ▼ LISTINGS                                                                 │
│     Listings                                   /listings                     │
│     Templates                                  /templates                    │
│     Bulk Create                                /listings/bulk       [P1]     │
│     SEO Assistant                              /listings/seo        [P1]     │
│                                                                             │
│  ▼ ORDERS                                                                   │
│     Orders                                     /orders                       │
│     Fulfillment                                /orders/fulfillment           │
│                                                                             │
│  ▼ PRICING & PROFITABILITY                                                  │
│     Calculator                                 /pricing                      │
│     Price Rules                                /pricing/rules                │
│                                                                             │
│  ▼ PROMOTIONS                     [P1]                                       │
│     Discounts                                  /discounts                    │
│                                                                             │
│  ▼ MOCKUPS & CUSTOMIZATION       [P1]                                        │
│     Mockup Studio                              /mockups                      │
│     Customization Templates                    /mockups/templates            │
│                                                                             │
│  ▼ DESIGN LIBRARY                 [P2]                                       │
│     Designs                                    /designs                      │
│     Design Mappings                            /designs/mappings             │
│                                                                             │
│  ▼ ANALYTICS                                                                 │
│     Overview                                   /analytics                    │
│     Product Performance                        /analytics/products   [P2]    │
│     Profitability Reports                      /analytics/profitability [P2] │
│                                                                             │
│  ─────────────────────────────────────────                                  │
│  Profile                                       /profile                     │
│  Billing                                       /settings/billing            │
│  Log out                                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Legend:** `[P1]` = Growth-phase; `[P2]` = Advanced-phase. **Connections** moved up; **Compare & switch** under Products; **Templates** under Listings; **Tools** removed.

---

## 2. Menu Structure (Hierarchical)

### 2.1 Overview

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Dashboard** | `/` | `LayoutDashboard` | MVP | Multi-store overview, quick stats, recent orders, low-stock alerts |

---

### 2.2 Products

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **My Products** | `/products` | `Package` | MVP | User’s product list; SKU tracking; variant management; add to listings |
| **Catalog (Add from Supplier)** | `/products/catalog` | `PackagePlus` | MVP | Browse PoD catalog by connection; add products to My Products (modal or dedicated view) |

**Sub-views / modals (no separate nav item):**
- Add Product (modal from Catalog or My Products)
- Product detail (variant/SKU editor, pricing, which listings use it)

---

### 2.3 Listings

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Listings** | `/listings` | `List` | MVP | Etsy & Shopify listings; create/edit; SKU ↔ listing variant mapping; inventory sync |
| **Bulk Create** | `/listings/bulk` | `Layers` | P1 | CSV import; template-based bulk creation; bulk image upload |
| **SEO Assistant** | `/listings/seo` | `Search` | P1 | Title/tag/description optimization; keyword suggestions; SEO scoring |

**Sub-views:**
- Listing detail (edit listing, variants, sync status)
- Create Listing wizard (product → store → options → publish)

**Context:** Listings can be filtered by **Shop** (Etsy / Shopify) and **Store** (multi-store).

---

### 2.4 Orders

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Orders** | `/orders` | `ShoppingCart` | MVP | Unified order list from Etsy + Shopify; status; customer; link to fulfillment |
| **Fulfillment** | `/orders/fulfillment` | `Truck` | MVP | Orders pending fulfillment; route to PoD; customization extraction; track status |

**Sub-views:**
- Order detail (items, customization, fulfillment status, tracking)
- Fulfillment queue (approve, retry, mark done)

---

### 2.5 Pricing & Profitability

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Calculator** | `/pricing` | `Calculator` | MVP | Fee calculator (Etsy/Shopify); margin; min profitable price; platform fee breakdown |
| **Price Rules** | `/pricing/rules` | `Sliders` | MVP | Per-product or per-variant pricing rules; markup; target margin; min price |

**Sub-views:**
- Price rule form (by product/variant, platform, rules)

---

### 2.6 Promotions – Discounts [P1]

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Discounts** | `/discounts` | `Percent` | P1 | Create/schedule programs; % or fixed; start/end; recurring; margin check; sync to Etsy/Shopify |

**Sub-views:**
- Program detail (products, schedule, performance)
- Create / Edit program wizard

**Plan limits:** See [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md) (e.g. 2 active programs for Starter, 5 for Growth, 15 for Scale).

---

### 2.7 Mockups & Customization [P1]

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Mockup Studio** | `/mockups` | `Image` | P1 | Create preview/production mockups; text, image, clipart layers; template picker |
| **Customization Templates** | `/mockups/templates` | `LayoutTemplate` | P1 | Manage placement templates (product × placement); reuse across listings |

**Sub-views:**
- Mockup editor (canvas, layers, export)
- Template editor

**Plan limits:** Mockups/month per plan (e.g. 100 Starter, 500 Growth, 2000 Scale).

---

### 2.8 Design Library [P2]

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Designs** | `/designs` | `Palette` | P2 | Upload, store, tag designs; versions; usage (listings/products) |
| **Design Mappings** | `/designs/mappings` | `GitBranch` | P2 | Map designs to products/placements; used in mockups and listings |

**Plan:** Growth / Scale (Design Library in subscription matrix).

---

### 2.9 Analytics

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Overview** | `/analytics` | `BarChart2` | MVP | Sales summary; revenue; orders; costs; fees; net profit; period selector |
| **Product Performance** | `/analytics/products` | `TrendingUp` | P2 | Performance by product/variant; views, orders, revenue, margin |
| **Profitability Reports** | `/analytics/profitability` | `DollarSign` | P2 | Margin by product/category; fee breakdown; trends |

**Context:** Filter by **Shop**, **Store**, **Supplier**, **Period**.

---

### 2.10 Connections

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Shops** | `/shops` | `Store` | MVP | Etsy & Shopify connections; connect/disconnect; sync; multi-store |
| **Suppliers** | `/suppliers` | `Truck` | MVP | Gelato, Printify, Printful; connect; sync catalog |

**Existing sub-routes:** `/shops/:shopId` (shop detail).  
**Plan limits:** Stores and suppliers per plan (e.g. 1 store Starter, 3 Growth, 10 Scale).

---

### 2.11 Compare & Switch (under Products)

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Compare & Switch** | `/comparison` | `GitCompare` | MVP | Compare same product across suppliers; switch supplier (single or bulk) |

---

### 2.12 Templates (under Listings)

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Templates** | `/templates` | `FileText` | MVP | Listing templates; default title/description/tags; link to products |
| *Template detail* | `/templates/:templateId` | — | MVP | Edit template; products in template; create listing |

---

### 2.13 User & Settings (Footer)

| Item | Route | Icon | Phase | Description |
|------|-------|------|--------|-------------|
| **Profile** | `/profile` | `User` | MVP | Account info; password; preferences |
| **Subscription & Billing** | `/settings/billing` | `CreditCard` | MVP | Current plan; usage (products, listings, orders, mockups); upgrade; billing history |

**Log out** – no route; action in header/sidebar.

---

## 3. Route Summary (Flat List)

| Route | Menu Item | Phase |
|-------|-----------|--------|
| `/` | Dashboard | MVP |
| `/products` | My Products | MVP |
| `/products/catalog` | Catalog (Add from Supplier) | MVP |
| `/listings` | Listings | MVP |
| `/listings/bulk` | Bulk Create | P1 |
| `/listings/seo` | SEO Assistant | P1 |
| `/orders` | Orders | MVP |
| `/orders/fulfillment` | Fulfillment | MVP |
| `/pricing` | Calculator | MVP |
| `/pricing/rules` | Price Rules | MVP |
| `/discounts` | Discounts | P1 |
| `/mockups` | Mockup Studio | P1 |
| `/mockups/templates` | Customization Templates | P1 |
| `/designs` | Designs | P2 |
| `/designs/mappings` | Design Mappings | P2 |
| `/analytics` | Analytics Overview | MVP |
| `/analytics/products` | Product Performance | P2 |
| `/analytics/profitability` | Profitability Reports | P2 |
| `/shops` | Shops | MVP |
| `/shops/:shopId` | Shop Detail | MVP |
| `/suppliers` | Suppliers | MVP |
| `/comparison` | Compare & Switch (under Products) | MVP |
| `/templates` | Templates (under Listings) | MVP |
| `/templates/:templateId` | Template Detail | MVP |
| `/profile` | Profile | MVP |
| `/settings/billing` | Billing | MVP |

---

## 4. Sidebar Section Grouping (revised)

Group menu items into **collapsible sections** in this order:

```
1. OVERVIEW
   └── Dashboard

2. CONNECTIONS
   └── Shops
   └── Suppliers

3. PRODUCTS
   └── My Products
   └── Catalog
   └── Compare & Switch

4. LISTINGS
   └── Listings
   └── Templates
   └── Bulk Create        [P1]
   └── SEO Assistant      [P1]

5. ORDERS
   └── Orders
   └── Fulfillment

6. PRICING & PROFITABILITY
   └── Calculator
   └── Price Rules

7. PROMOTIONS             [P1]
   └── Discounts

8. MOCKUPS & CUSTOMIZATION [P1]
   └── Mockup Studio
   └── Customization Templates

9. DESIGN LIBRARY         [P2]
   └── Designs
   └── Design Mappings

10. ANALYTICS
    └── Overview
    └── Product Performance    [P2]
    └── Profitability Reports  [P2]

USER (footer)
    └── Profile
    └── Billing
    └── Log out
```

**Removed:** Standalone **Tools** section (Compare → Products, Templates → Listings).  
Sections 7, 8, 9 can be **hidden or disabled** when the plan doesn’t include them (see [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md)).

---

## 5. Cross-Linking & Shortcuts

- **Dashboard** → quick links to Orders (pending), Listings (low stock), Analytics (this month).
- **My Products** → “Add from catalog” → Catalog filtered by chosen supplier.
- **Listings** → “Create listing” wizard: pick product (from My Products) → pick store → set options → optionally open SEO Assistant.
- **Orders** → “Fulfill” → Fulfillment queue or order-specific fulfillment flow.
- **Calculator** → link from product/listing price setup and from Price Rules.
- **Discount Programs** → link from product/listing when attaching to a program.
- **Mockup Studio** → open from listing editor (preview) or Design Library (design → mockup).

---

## 6. Mobile & Small Screens

- **Hamburger menu** opens sidebar (same structure).
- **Bottom nav** (optional): Dashboard | Products | Orders | More (overflow).
- **“More”** exposes Listings, Pricing, Discounts, Mockups, Design Library, Analytics, Connections, Compare, Templates, Settings.

---

## 7. Implementation Notes

- **Layout**: Reuse existing `Layout` + sidebar; extend `navigation` with sections and nested items.
- **Routing**: Add routes in `App.tsx` for new paths; use nested routes under `/listings`, `/orders`, `/pricing`, `/discounts`, `/mockups`, `/designs`, `/analytics`, `/settings` as above.
- **Plan gating**: Hide or disable P1/P2 menu items (and redirect) when plan doesn’t include them; show upgrade CTA where relevant.
- **Store context**: Optional global “Current store” switcher in header when multi-store; filter Listings, Orders, Analytics by store.

---

---

## 8. Sidebar Wireframe (Desktop, revised)

```
┌──────────────────────────────────────┐
│  POD Manager                         │
├──────────────────────────────────────┤
│  ▼ OVERVIEW                          │
│    📊 Dashboard                      │
│  ▼ CONNECTIONS                       │
│    🏪 Shops                          │
│    🚚 Suppliers                      │
│  ▼ PRODUCTS                          │
│    📦 My Products                    │
│    ➕ Catalog                        │
│    ⚖️ Compare & Switch               │
│  ▼ LISTINGS                          │
│    📋 Listings                       │
│    📄 Templates                      │
│    📚 Bulk Create          [P1]      │
│    🔍 SEO Assistant        [P1]      │
│  ▼ ORDERS                            │
│    🛒 Orders                         │
│    🚚 Fulfillment                    │
│  ▼ PRICING & PROFITABILITY           │
│    🧮 Calculator                     │
│    ⚙️ Price Rules                    │
│  ▼ PROMOTIONS             [P1]       │
│    % Discounts                       │
│  ▼ MOCKUPS & CUSTOMIZATION [P1]      │
│    🖼️ Mockup Studio                  │
│    📐 Customization Templates        │
│  ▼ DESIGN LIBRARY         [P2]       │
│    🎨 Designs                        │
│    🔀 Design Mappings                │
│  ▼ ANALYTICS                         │
│    📈 Overview                       │
│    📊 Product Performance   [P2]     │
│    💰 Profitability          [P2]    │
├──────────────────────────────────────┤
│  👤 User Name                        │
│     user@email.com                   │
│  [Profile] [Billing] [Log out]       │
└──────────────────────────────────────┘
```

---

**Document version:** 1.0  
**Last updated:** 2025-01-23
