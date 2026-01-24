# PoD Shop Manager – Detailed Implementation Plan

**Role:** Product Manager  
**Last updated:** 2025-01  
**Sources:** PRODUCT_PLAN, SUBSCRIPTION_PLANS, FEATURE_PRIORITY, UI_MENU_STRUCTURE; Etsy/Shopify/PoD seller forums, Reddit, community feedback; competitor and tool research.

---

## How to Read This Document

- **Problem:** What pain point or need exists.  
- **Required:** What must be built (scope).  
- **User goal:** What sellers want to achieve.  
- **Status:** `X%` = current implementation level (backend + frontend + integrations).  
- **Phase:** MVP (P0) | Growth (P1) | Advanced (P2).

---

## 1. Authentication & Account

### 1.1 Email/password registration and login  
**Problem:** Sellers need a simple way to sign up and sign in without OAuth.  
**Required:** Register (email, password), login, JWT access + refresh, logout, secure password storage.  
**User goal:** Create an account and use the app with email/password.  
**Status:** **95%**  
**Phase:** P0  

*Remaining: Email verification flow, password reset.*

---

### 1.2 OAuth login (Google, Etsy, Shopify)  
**Problem:** Many sellers prefer “Sign in with Google” or use Etsy/Shopify daily; separate passwords add friction.  
**Required:** OAuth authorize + callback for Google, Etsy, Shopify; link or create user; store tokens; handle refresh.  
**User goal:** Sign in with one click via Google or marketplace accounts.  
**Status:** **90%**  
**Phase:** P0  

*Remaining: Robust token refresh, error handling, and account linking UX.*

---

### 1.3 User profile and preferences  
**Problem:** Sellers need to update name, avatar, and app preferences (e.g. theme).  
**Required:** GET/PATCH profile (name, avatar, theme, etc.); optional password/email change; persist preferences.  
**User goal:** Customize profile and app experience (e.g. theme selection).  
**Status:** **85%**  
**Phase:** P0  

*Profile CRUD and theme preference exist; expand validation and UI as needed.*

---

### 1.4 Subscription & billing  
**Problem:** Sellers need clear pricing, plan comparison, usage visibility, and the ability to subscribe, upgrade, or cancel.  
**Required:** Plan comparison (Free Trial, Starter, Pro, Master); usage vs limits; monthly/yearly toggle; proration; start trial; upgrade/downgrade; cancel auto-renew; payment UI (actual processor TBD).  
**User goal:** Choose a plan, see usage, pay, and cancel without confusion.  
**Status:** **75%**  
**Phase:** P0  

*Plans, usage, trial, upgrade logic, and pay/cancel UX exist; payment processing not connected.*

---

## 2. Connections (Shops & Suppliers)

### 2.1 Connect Etsy shops  
**Problem:** Sellers run Etsy shops; the app must access listings, orders, and inventory.  
**Required:** Etsy OAuth; fetch user’s shops; store shop + tokens; list connected shops; disconnect.  
**User goal:** Connect Etsy shop(s) so the app can manage listings and orders.  
**Status:** **80%**  
**Phase:** P0  

*OAuth and connect exist; ensure multiple shops and token refresh.*

---

### 2.2 Connect Shopify stores  
**Problem:** Sellers use Shopify; the app needs the same capabilities as for Etsy.  
**Required:** Shopify OAuth (install app); store shop domain + token; list connected stores; disconnect; handle app uninstall webhook.  
**User goal:** Connect Shopify store(s) for product and order management.  
**Status:** **75%**  
**Phase:** P0  

*OAuth and connect exist; verify webhooks and multi-store.*

---

### 2.3 Connect PoD suppliers (Gelato, Printify, Printful)  
**Problem:** Sellers use one or more PoD providers; the app must sync catalogs and fulfill orders.  
**Required:** Per-supplier auth (API key or OAuth); connect/disconnect; sync catalog; list connections.  
**User goal:** Connect Gelato, Printify, and/or Printful to compare and fulfill.  
**Status:** **70%**  
**Phase:** P0  

*Connect and catalog sync exist; Printify/Printful timeouts and edge cases reported; streamline.*

---

### 2.4 Multi-store dashboard and unified view  
**Problem:** Managing several Etsy + Shopify stores is scattered and time-consuming.  
**Required:** Single dashboard showing all connected shops; KPIs (listings, orders, revenue) per shop and combined; quick links to Listings, Orders, Analytics.  
**User goal:** See all stores in one place and jump into management.  
**Status:** **50%**  
**Phase:** P0  

*Dashboard and layout exist; need richer per-shop stats and clearer “unified” narrative.*

---

## 3. Products & Catalog

### 3.1 My Products – product list and SKU tracking  
**Problem:** PoD sellers lose track of which products they sell, where, and under which SKUs; SKU mismatches cause overselling and fulfillment errors.  
**Required:** List user’s products; show SKU, supplier, variants (size/color); link to listings; add from catalog; basic search/filter.  
**User goal:** Central list of “my products” with SKUs for inventory and fulfillment.  
**Status:** **65%**  
**Phase:** P0  

*User products, catalog add, and comparison exist; variant-level SKU clarity and listing links need strengthening.*

---

### 3.2 Catalog – add products from supplier  
**Problem:** Sellers must add PoD products from supplier catalogs before they can list or compare.  
**Required:** Browse Gelato/Printify/Printful catalogs by connection; search, filter; add to My Products with supplier + product ID; handle pagination and loading.  
**User goal:** Easily add supplier products to “My Products” without leaving the app.  
**Status:** **60%**  
**Phase:** P0  

*Catalog fetch and add exist; timeouts and UX polish needed.*

---

### 3.3 Variant-level SKU mapping (size × color × design)  
**Problem:** Each variant (e.g. M, Navy, Design A) must map to the correct supplier SKU; errors cause wrong fulfillment or overselling.  
**Required:** Store and display SKU per variant; map variants to Etsy/Shopify listing options; validate uniqueness; support custom SKU templates (future).  
**User goal:** Reliable variant ↔ SKU mapping across platform listings and suppliers.  
**Status:** **45%**  
**Phase:** P0  

*Comparison and switching use SKUs; explicit variant-level mapping and validation incomplete.*

---

### 3.4 Supplier comparison – compare prices across PoD  
**Problem:** Same product can have different base + shipping costs across Gelato, Printify, Printful; sellers miss savings.  
**Required:** For each “my product,” fetch equivalent offerings from connected suppliers; show base price, shipping, total; highlight cheapest; filter by shop, product type, supplier.  
**User goal:** Compare PoD costs and choose the best supplier per product.  
**Status:** **70%**  
**Phase:** P0  

*Compare API and UI exist; matching logic and edge cases need refinement.*

---

### 3.5 One-click supplier switch  
**Problem:** After comparing, sellers want to switch supplier without manually re-listing or editing everywhere.  
**Required:** Switch product to target supplier; update SKUs; push updates to Etsy/Shopify listings (or mark for sync); preserve listing connection.  
**User goal:** Change PoD supplier with minimal manual work.  
**Status:** **55%**  
**Phase:** P0  

*Switch and Etsy/Shopify SKU updates exist; bulk switch and rollback UX need work.*

---

### 3.6 Bulk supplier switch  
**Problem:** Switching many products one-by-one is slow and error-prone.  
**Required:** Select multiple products; choose target supplier; bulk switch; report success/failure; optionally revert.  
**User goal:** Migrate many products to a new supplier in one action.  
**Status:** **40%**  
**Phase:** P0  

*Bulk switch endpoint exists; UI and batch feedback are minimal.*

---

## 4. Listings

### 4.1 Listings – list and view Etsy & Shopify listings  
**Problem:** Sellers need a single place to see all listings across Etsy and Shopify.  
**Required:** List listings with title, shop, SKU, price, status; filter by shop, search; pagination; link to shop/listing detail.  
**User goal:** Overview of all listings and quick access to edit or sync.  
**Status:** **60%**  
**Phase:** P0  

*Listings API and UI exist; sync from Etsy/Shopify powers data; create/edit flows largely via templates.*

---

### 4.2 Listing sync from Etsy and Shopify  
**Problem:** Listings change on Etsy/Shopify; the app must stay in sync to avoid stale data.  
**Required:** Sync listings (and variants) from connected Etsy shops and Shopify stores; map to internal products; update SKU, price, quantity; handle pagination and rate limits.  
**User goal:** App always reflects current Etsy/Shopify listings.  
**Status:** **65%**  
**Phase:** P0  

*Etsy and Shopify sync implemented; sync-on-schedule and conflict handling can be improved.*

---

### 4.3 Create single listing (from template or wizard)  
**Problem:** Sellers create listings one-by-one; they want a guided flow rather than raw API calls.  
**Required:** Create listing from template (products, options, default title/tags) or wizard (product → store → details → publish); support Etsy and Shopify; map variants/SKUs.  
**User goal:** Create Etsy/Shopify listings from the app with less manual work.  
**Status:** **50%**  
**Phase:** P0  

*Template-based create-listing exists; wizard UX and validation need expansion.*

---

### 4.4 Bulk listing creation (CSV import)  
**Problem:** Creating dozens or hundreds of listings manually takes days; sellers use CSV in other tools.  
**Required:** CSV/Excel import; map columns to title, description, tags, variants, images, etc.; validate; preview; bulk create to Etsy/Shopify; report errors.  
**User goal:** Upload a spreadsheet and create many listings at once.  
**Status:** **0%**  
**Phase:** P1  

*Placeholder page only; no backend.*

---

### 4.5 Bulk image upload and mockup association  
**Problem:** Listing creation often requires many images; associating them to products/variants manually is tedious.  
**Required:** Upload multiple images; assign to products/variants or listings; optional link to mockup flow; store and reuse.  
**User goal:** Batch-upload images and attach them to listings efficiently.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

### 4.6 SEO Assistant – title, tags, description optimization  
**Problem:** Poor SEO is a top reason PoD shops fail; Etsy rewards full 140-char titles, 13 tags, strong descriptions.  
**Required:** Keyword/tag suggestions (Etsy-aware); title optimizer (use full length); description templates; SEO “score” per listing; apply or copy to listing.  
**User goal:** Improve discoverability and search ranking without being an SEO expert.  
**Status:** **0%**  
**Phase:** P1  

*Placeholder page only; no backend.*

---

## 5. Orders & Fulfillment

### 5.1 Order sync from Etsy and Shopify  
**Problem:** Orders stay on Etsy/Shopify; the app can’t fulfill or report accurately without them.  
**Required:** Fetch orders (and receipts) from connected Etsy shops and Shopify stores; normalize into app orders; store items, customer, shipping; incremental sync and webhooks.  
**User goal:** All Etsy and Shopify orders visible in the app.  
**Status:** **15%**  
**Phase:** P0  

*Order model and list API exist; no Etsy/Shopify order fetch or webhooks.*

---

### 5.2 Orders list and detail  
**Problem:** Sellers need to see and inspect orders in one place.  
**Required:** List orders with filters (platform, shop, status, date); pagination; order detail (items, customer, shipping, status, fulfillment); link to fulfillment.  
**User goal:** View and search orders across platforms.  
**Status:** **55%**  
**Phase:** P0  

*Orders list and detail API + UI exist; data is empty without order sync.*

---

### 5.3 Fulfillment queue – orders pending fulfillment  
**Problem:** Sellers must identify which orders still need to be sent to PoD.  
**Required:** List orders/items in “pending” or “processing”; show customer, items, destination; actions: “Fulfill,” “Skip,” “Cancel”; link to fulfillment flow.  
**User goal:** Work through unfulfilled orders quickly.  
**Status:** **40%**  
**Phase:** P0  

*Fulfillment API and simple UI exist; no “fulfill” action to PoD yet.*

---

### 5.4 Auto-route orders to PoD supplier by SKU  
**Problem:** Manual routing is slow and error-prone; each item should go to the right supplier based on SKU.  
**Required:** Map SKU → supplier (and product/variant); on “Fulfill,” build PoD order payload; call Gelato/Printify/Printful create-order; record fulfillment; update Etsy/Shopify status/tracking.  
**User goal:** Orders automatically route to the correct PoD supplier.  
**Status:** **20%**  
**Phase:** P0  

*Supplier create-order APIs exist; routing and full flow not wired.*

---

### 5.5 Customization data extraction (e.g. from Etsy personalization)  
**Problem:** Custom print (text, image) comes as Etsy/Shopify personalization; PoD needs it for production.  
**Required:** Parse personalization from order; map to mockup/customization fields; pass to PoD order (e.g. print files or customization payload).  
**User goal:** Personalized orders automatically include the right print data.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

### 5.6 Fulfillment status and tracking sync  
**Problem:** Sellers need to know when an order is produced and shipped, and to show customers tracking.  
**Required:** Poll or webhook from PoD for status updates; store tracking number and status; push to Etsy/Shopify; show in order/fulfillment UI.  
**User goal:** Track fulfillment and keep customers updated.  
**Status:** **5%**  
**Phase:** P0  

*Fulfillment model exists; no supplier status/tracking integration.*

---

## 6. Inventory

### 6.1 Real-time inventory sync across Etsy and Shopify  
**Problem:** Selling on multiple channels causes overselling when inventory isn’t unified.  
**Required:** Single source of truth per product/variant; propagate quantity updates to Etsy and Shopify; respect each platform’s rules; handle sync failures.  
**User goal:** Never oversell; inventory consistent everywhere.  
**Status:** **25%**  
**Phase:** P0  

*Listing sync updates products; no explicit “inventory sync” or quantity push.*

---

### 6.2 Low-stock alerts  
**Problem:** Sellers get caught by stockouts without warning.  
**Required:** Configurable thresholds per product or globally; alerts (in-app, email) when stock &lt; threshold; link to replenish or adjust listing.  
**User goal:** Act before stock runs out.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

### 6.3 Auto-deactivate listing when out of stock  
**Problem:** Listings stay active with 0 stock, leading to cancelled orders and bad reviews.  
**Required:** When quantity = 0, deactivate or hide listing on Etsy/Shopify (or mark “out of stock”); optional re-activate when restocked.  
**User goal:** Avoid selling what they can’t fulfill.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

## 7. Pricing & Profitability

### 7.1 Fee calculator (Etsy & Shopify)  
**Problem:** Sellers misestimate fees and set unprofitable prices; Etsy has listing, transaction, payment, offsite ads; Shopify has transaction and payment fees.  
**Required:** Calculator: platform, price, cost, optional offsite ads; output fees, net profit, margin %; support Etsy tiers (e.g. offsite 12% vs 15%).  
**User goal:** Know true profit before pricing.  
**Status:** **75%**  
**Phase:** P0  

*Pricing calculator API and UI exist; extend for all fee types and edge cases.*

---

### 7.2 Min profitable price and margin targets  
**Problem:** Sellers want to hit a target margin (e.g. 20%) or avoid selling below cost.  
**Required:** Given cost and target margin (or min profit), compute min price; suggest price for target margin; show margin at current price.  
**User goal:** Price confidently to meet profit goals.  
**Status:** **50%**  
**Phase:** P0  

*Calculator has cost/price; min-price and target-margin UX need emphasis.*

---

### 7.3 Price rules (markup, margin, min price per product)  
**Problem:** Sellers apply different margins by product or category; manual calculation doesn’t scale.  
**Required:** Define rules per product/variant: markup %, target margin, or min price; apply when calculating; optional bulk apply.  
**User goal:** Automate pricing logic per product.  
**Status:** **45%**  
**Phase:** P0  

*Price rules CRUD exists; tight integration with calculator and listings needs work.*

---

### 7.4 Historical profitability and margin reports  
**Problem:** Sellers need to see actual margins and profitability over time, not just estimates.  
**Required:** Use orders + costs + fees; compute profit and margin per order/item; aggregate by product, category, period; expose in Analytics.  
**User goal:** Understand which products and periods are profitable.  
**Status:** **15%**  
**Phase:** P1  

*Analytics profitability placeholder; no cost/fee data or reports.*

---

## 8. Discounts

### 8.1 Discount programs (create, edit, delete)  
**Problem:** Sellers run sales and promos; managing them manually is cumbersome.  
**Required:** Create program (name, type %, fixed, BOGO; value; dates); edit; delete; list programs; active/inactive.  
**User goal:** Define discount campaigns in one place.  
**Status:** **60%**  
**Phase:** P1  

*Discount CRUD and list UI exist; scheduling and platform sync missing.*

---

### 8.2 Schedule discounts (start/end, recurrence)  
**Problem:** Etsy has limited native scheduling; sellers want flash sales and recurring promos without manual toggle.  
**Required:** Set start/end date-time; optional recurrence (daily, weekly, etc.); auto-activate/deactivate; timezone handling.  
**User goal:** Run scheduled and recurring sales automatically.  
**Status:** **20%**  
**Phase:** P1  

*DB supports dates; no scheduling engine or UI.*

---

### 8.3 Margin check before applying discount  
**Problem:** Discounts can push products below cost; sellers want a safety check.  
**Required:** Before applying discount, compute effective price and margin; warn or block if below min margin; optionally allow override.  
**User goal:** Avoid unprofitable promotions.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

### 8.4 Create discounts on Etsy and Shopify  
**Problem:** Discounts live on Etsy/Shopify; creating them manually duplicates work.  
**Required:** Sync program to Etsy (sales, coupons) and Shopify (discount codes, etc.); create/update/end per platform; map our program to platform entities.  
**User goal:** Run the same promotion on all stores with one action.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

### 8.5 Discount performance (revenue impact, conversion lift)  
**Problem:** Sellers can’t tell which promos actually help.  
**Required:** Track orders and revenue during active programs; compare to baseline; simple report (revenue, units, conversion) per program.  
**User goal:** Optimize future promotions.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

## 9. Customization & Mockups

### 9.1 Mockup Studio – create preview mockups  
**Problem:** Sellers need product images with designs for listings and marketing; external tools are costly.  
**Required:** In-app mockup flow: pick product, upload design, place on product (template); generate preview image; optional bulk.  
**User goal:** Create listing-ready mockups without leaving the app.  
**Status:** **0%**  
**Phase:** P1  

*Placeholder only; own mockup implementation per PRODUCT_PLAN.*

---

### 9.2 Customization templates (product × placement)  
**Problem:** Same placement rules (e.g. “front,” “back”) apply across products; redefining each time is redundant.  
**Required:** Define templates (product type × placement, dimensions, safe zones); reuse in mockup and listing flows.  
**User goal:** Consistent mockups and fewer repetitive settings.  
**Status:** **0%**  
**Phase:** P1  

*Placeholder only.*

---

### 9.3 Production-ready file generation  
**Problem:** PoD suppliers need print-ready files (resolution, format, bleed).  
**Required:** Export mockup/customization as print-ready asset (e.g. PNG/PDF); optional attach to order when fulfilling.  
**User goal:** Send correct files to PoD automatically.  
**Status:** **0%**  
**Phase:** P1  

*Not started.*

---

### 9.4 Customer-facing real-time preview (optional)  
**Problem:** Shoppers want to see customization before buying; that can improve conversion.  
**Required:** Embeddable or linkable preview; customer adjusts text/image; see mockup update; pass customization to order.  
**User goal:** Higher conversion through “see before you buy.”  
**Status:** **0%**  
**Phase:** P1  

*Not started; larger scope.*

---

## 10. Design Library (P2)

### 10.1 Design upload and storage  
**Problem:** Designs are scattered (local, Canva, etc.); reusing them is awkward.  
**Required:** Upload designs (images, etc.); store in app; thumbnails; organize by name, tags; search.  
**User goal:** Central design library.  
**Status:** **0%**  
**Phase:** P2  

*Placeholder only.*

---

### 10.2 Design–product mapping  
**Problem:** Sellers need to know which designs go on which products and placements.  
**Required:** Map design → product (or product type) and placement; use in mockup and listing creation.  
**User goal:** Reuse designs across products consistently.  
**Status:** **0%**  
**Phase:** P2  

*Placeholder only.*

---

### 10.3 Version control and design performance  
**Problem:** Designs evolve; sellers want history and basic performance data.  
**Required:** Versions per design; “which designs sell best” metrics (e.g. revenue, units).  
**User goal:** Iterate on designs and double down on winners.  
**Status:** **0%**  
**Phase:** P2  

*Not started.*

---

## 11. Analytics & Reporting

### 11.1 Analytics overview (revenue, orders, profit)  
**Problem:** Sellers need a quick summary of performance.  
**Required:** Period selector (7d, 30d, 90d); revenue, orders, listings, net profit; use real order/listings data.  
**User goal:** Know how the business is doing at a glance.  
**Status:** **50%**  
**Phase:** P0  

*Overview API and UI exist; orders often empty without sync; costs/fees not fully integrated.*

---

### 11.2 Product performance (views, orders, revenue, margin)  
**Problem:** Sellers want to see which products drive sales and profit.  
**Required:** Per-product (or variant) metrics: views, orders, revenue, cost, margin; filter by period, shop, product type; sort and export.  
**User goal:** Focus on best sellers and fix or drop weak products.  
**Status:** **5%**  
**Phase:** P2  

*Placeholder API; no views or product-level analytics.*

---

### 11.3 Profitability reports (by product, category, period)  
**Problem:** Profitability is more than revenue; sellers need margin and cost breakdown.  
**Required:** Reports by product, category, and period; cost, fees, profit, margin %; trends over time.  
**User goal:** Understand true profitability by segment.  
**Status:** **5%**  
**Phase:** P2  

*Placeholder API; no cost/fee or reporting logic.*

---

### 11.4 Sales trends and simple forecasting  
**Problem:** Sellers plan inventory and promos; raw numbers alone aren’t enough.  
**Required:** Trend charts (revenue, orders over time); optional simple forecast (e.g. next 30 days); export.  
**User goal:** Spot trends and plan ahead.  
**Status:** **0%**  
**Phase:** P2  

*Not started.*

---

## 12. Templates & Compare

### 12.1 Listing templates (defaults, products, create listing)  
**Problem:** Similar listings share structure; re-entering everything is slow.  
**Required:** Create template (default title, description, tags, category); add products, sizes, colors; create listing from template to Etsy/Shopify.  
**User goal:** Reuse structures and ship new listings faster.  
**Status:** **65%**  
**Phase:** P0  

*Templates CRUD, products, create-listing flow exist; wizard and validation can be improved.*

---

### 12.2 Compare Products (supplier comparison UI)  
**Problem:** Sellers need a clear UI to compare PoD offerings and switch.  
**Required:** Compare view (products, suppliers, prices, savings); filters; switch action; bulk switch.  
**User goal:** Compare and switch suppliers without spreadsheets.  
**Status:** **70%**  
**Phase:** P0  

*Comparison page and switch exist; bulk and edge cases need work.*

---

## 13. Tax & Compliance (P2)

### 13.1 Tax calculation by region  
**Problem:** Tax rules vary by region; manual calculation is error-prone.  
**Required:** Configure tax rules by region; calculate tax at checkout or in reports; optional integration with tax provider.  
**User goal:** Correct tax collection and reporting.  
**Status:** **0%**  
**Phase:** P2  

*Not started.*

---

### 13.2 VAT and compliance reporting  
**Problem:** Sellers in EU and others must handle VAT and compliance.  
**Required:** VAT-inclusive options; basic compliance reports (e.g. EU VAT); export for accountants.  
**User goal:** Stay compliant with minimal manual work.  
**Status:** **0%**  
**Phase:** P2  

*Not started.*

---

## 14. Infrastructure & Quality

### 14.1 Plan-gating (limits, overages)  
**Problem:** Features and usage must match subscription tier.  
**Required:** Enforce limits (stores, products, listings, orders, mockups, storage, etc.); overage handling or upgrade prompts; usage visible in billing.  
**User goal:** Clear rules and no surprise overages.  
**Status:** **55%**  
**Phase:** P0  

*Plans, usage records, and billing UI exist; enforcement across all features incomplete.*

---

### 14.2 API access (read-only / full)  
**Problem:** Power users want to integrate with other tools.  
**Required:** API keys or scoped access; read-only vs read-write by plan; rate limits; docs.  
**User goal:** Automate and integrate beyond the UI.  
**Status:** **0%**  
**Phase:** P2  

*Not started.*

---

### 14.3 Error tracking, logging, and monitoring  
**Problem:** Failures in sync, fulfillment, or APIs go unseen without monitoring.  
**Required:** Structured logging; error tracking (e.g. Sentry); basic health checks; alerts for critical failures.  
**User goal:** Reliable app and quick fixes when something breaks.  
**Status:** **30%**  
**Phase:** P0  

*Some logging; no centralized error tracking or alerting.*

---

### 14.4 E2E and integration tests  
**Problem:** Regressions in auth, sync, or payment are costly.  
**Required:** E2E tests for critical flows (login, connect, create listing, etc.); integration tests for Etsy/Shopify/PoD APIs (mocked or sandbox).  
**User goal:** Fewer bugs and safer deployments.  
**Status:** **15%**  
**Phase:** P0  

*TestScripts for ad-hoc checks; no automated E2E/integration suite.*

---

## 15. Summary by Phase

| Phase | Features | Avg. status |
|-------|----------|-------------|
| **P0 (MVP)** | Auth, connections, products, listings, orders, fulfillment, inventory, pricing, templates, compare, billing, dashboard, plan-gating | **~45%** |
| **P1 (Growth)** | Bulk listing, SEO, discounts (full), mockups, customization, order sync, fulfillment automation, inventory alerts | **~10%** |
| **P2 (Advanced)** | Design library, product/profitability analytics, tax, API, forecasting | **~2%** |

---

## 16. Suggested Implementation Order

1. **Order sync** from Etsy & Shopify (unblocks fulfillment and analytics).  
2. **Fulfillment flow** end-to-end: route by SKU → PoD create order → status/tracking.  
3. **Inventory sync** and quantity push; then **low-stock** and **auto-deactivate**.  
4. **Bulk listing** (CSV) and **SEO Assistant**.  
5. **Discount** scheduling, margin check, and **platform sync** (Etsy/Shopify).  
6. **Mockup Studio** and **customization templates** (own implementation).  
7. **Design library** and **design–product mapping**.  
8. **Product performance** and **profitability** reports.  
9. **Tax** and **compliance** basics.  
10. **API access** and **monitoring** improvements.

---

**Document version:** 1.0  
**Owner:** Product Manager  
**References:** PRODUCT_PLAN.md, SUBSCRIPTION_PLANS.md, FEATURE_PRIORITY.md, UI_MENU_STRUCTURE.md, COMPETITOR_ANALYSIS.md.
