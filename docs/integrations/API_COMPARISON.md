# Etsy vs Shopify vs Our API — Comparison

This document compares:

1. **Etsy Open API v3**
2. **Shopify Admin API (GraphQL)**
3. **Our API** (PoD ShopManager backend)

The goal is to show where the **data models differ**, where we **abstract**, and what **gaps** exist for requested features.

## Quick comparison table

| Dimension | Etsy Open API v3 | Shopify Admin API (GraphQL) | Our API (today) |
|---|---|---|---|
| **Protocol** | REST | GraphQL | REST |
| **Base URL** | `https://api.etsy.com/v3/application` | `https://{shop}.myshopify.com/admin/api/2026-01/graphql.json` | `https://{our-backend}/api` |
| **Auth** | OAuth 2.0 + PKCE required | OAuth / Admin tokens; `X-Shopify-Access-Token` | JWT for app users; stores connected via OAuth tokens we store |
| **Rate limiting** | QPS+QPD sliding window; headers + `retry-after` | GraphQL cost bucket; max single query cost 1000; bulk ops for large exports | Depends on our hosting + any rate limiting middleware (we should add explicit limits) |
| **Webhooks** | Limited; currently `ORDER_PAID` (commercial apps only) | Many topics; filters + payload modification | Not implemented as a public webhook platform; we should consume Etsy/Shopify webhooks |
| **Catalog model** | Listing (+ ListingInventory variants) | Product + ProductVariant | We store shop listings as `Product`/`ProductVariant` (local DB) and expose list endpoints |
| **Order model** | Receipt + Transaction (line) | Order + LineItem; FulfillmentOrder workflow | `Order` + `OrderItem` + `Fulfillment` (local DB) |
| **Inventory model** | Listing inventory offerings (limited) | InventoryItem + multi-location InventoryLevel | Not yet fully modeled; we currently treat inventory mostly as a field on variants |
| **SEO fields** | title/description/tags; platform-specific constraints | SEO object + handle + tags + collections | We’ll expose “SEO suggestions” + patch operations; platform adapters apply changes |

## Core model differences (what must be abstracted)

### Listings vs products

- **Etsy**
  - “Listing” is the primary catalog item.
  - Variants come from “ListingInventory” (products + offerings).
  - SKU may be absent at listing root; often per-inventory “product”.

- **Shopify**
  - “Product” is the container; “ProductVariant” is the sellable SKU.
  - SKU is native on `ProductVariant.sku`.
  - Publishing state and sales channels are richer; many more commerce features (discounts, metafields, markets).

**Our abstraction**: `Listing` with `variants[]`, where variant SKU is first-class and may be null on Etsy if missing.

### Orders & fulfillment

- **Etsy**
  - Orders: `Receipt` (header) and `Transaction` (line items).
  - Fulfillment workflows and tracking support vary by endpoints/scopes.
  - Webhooks are limited.

- **Shopify**
  - Orders: rich object with financial and fulfillment statuses.
  - Fulfillment uses `FulfillmentOrder` (what needs to be shipped) and `Fulfillment` (shipment).
  - Strong webhook ecosystem.

**Our abstraction**: `Order` (financialStatus + fulfillmentStatus) + `OrderLineItem[]` + `Fulfillment[]`, with platform-specific details in `platformData`.

## Our API (current state) — what we expose today

This is derived from our current Flask blueprints (see `backend/app/blueprints/**/routes.py`). Our API is primarily:

- A **user-facing API** (JWT auth)
- With **store connection** endpoints for Etsy/Shopify
- A **unified listings view** (local DB products)
- Orders endpoints (local DB orders)
- PoD supplier comparison/switching

### Auth

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- OAuth helper endpoints (redirect flows) under `/api/auth/*/authorize` and `/api/auth/*/callback` for:
  - Etsy, Shopify (and also Google + suppliers: Printify/Printful/Gelato)

### Shops (store connections)

- `GET /api/shops`
- `GET /api/shops/<shop_id>`
- `POST /api/shops/etsy/connect`
- `POST /api/shops/shopify/connect`
- `POST /api/shops/<shop_id>/disconnect`
- `DELETE /api/shops/<shop_id>/delete`
- `POST /api/shops/<shop_id>/sync`
- `GET /api/shops/<shop_id>/products`
- `GET /api/shops/<shop_id>/products/<product_id>`

### Listings (unified “shop products”)

- `GET /api/listings` (supports `page`, `per_page`, `shop_id`, `supplier`, `search`)
- `GET /api/listings/<listing_id>`

### Orders

- `GET /api/orders` (supports `page`, `per_page`, `platform`, `shop_id`, `status`)
- `GET /api/orders/fulfillment`
- `GET /api/orders/<order_id>`

### Pricing & discounts (our value-add over platforms)

- `GET|POST /api/pricing/calculator` (Etsy/Shopify fee calculator)
- `GET|POST|PATCH|DELETE /api/pricing/rules[...]`
- `GET|POST|PATCH|DELETE /api/discounts[...]`

### Analytics

- `GET /api/analytics/overview`
- `GET /api/analytics/products` (placeholder)
- `GET /api/analytics/profitability` (placeholder)

### PoD supplier comparison (non-Etsy/Shopify)

- `GET /api/products/compare`
- `GET /api/products/compare/summary`
- `GET /api/products/compare/<product_id>`
- `POST /api/products/switch`

## How our API differs from Etsy & Shopify

### 1) Our API is “workflow-first”, not “platform-primitive-first”

- Etsy/Shopify expose primitives (Listing/Product, Receipt/Order).
- We expose workflows:
  - “list unified listings”
  - “compare suppliers”
  - “pricing rules”
  - “discount programs”

### 2) We unify multi-platform data

- Etsy and Shopify APIs are store/platform-specific.
- Our `/api/listings` merges listings across all connected shops (platform-agnostic).

### 3) We currently don’t expose a canonical “UnifiedStoreAdapter” API surface yet

We have partial surfaces:

- Store connect + sync are present (`/api/shops/*`).
- Listings/orders are read-only (mostly) via our DB.

**Missing to meet the requested features**:

- Write operations that apply to both platforms through a single shape:
  - Update listing/product title/description/tags/SEO
  - Bulk create listings/products
  - Publish/unpublish controls
  - Fulfillment actions (tracking upload / mark shipped)
  - Discount creation on platform (Shopify has rich discount APIs; Etsy is more limited)

### 4) Webhooks consumption

- Shopify: we should subscribe to order/product webhooks.
- Etsy: limited to `ORDER_PAID` (commercial apps).
- Our API should offer:
  - `/api/integrations/{platform}/webhooks/receive` endpoints
  - Signature verification (Etsy signing; Shopify HMAC for HTTPS delivery)
  - Event persistence + replay tools

## Recommended next step

Implement adapters to conform to the interface in `UNIFIED_COMMERCE_MODEL.md`, then refactor backend routes so UI consumes:

- `GET /api/stores` (connections)
- `GET /api/stores/:id/listings`
- `PATCH /api/stores/:id/listings/:listingId`
- `GET /api/stores/:id/orders`
- `POST /api/stores/:id/orders/:orderId/fulfillments`

while platform-specific logic stays behind the adapters.

