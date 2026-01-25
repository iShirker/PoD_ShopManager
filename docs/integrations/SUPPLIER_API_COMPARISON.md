# Printify vs Printful vs Gelato vs Our Supplier API — Comparison

This document compares:

1. **Printify API (v1)**
2. **Printful API (v1 + v2 beta notes)**
3. **Gelato APIs (multi-service: v3/v4/v1 hosts)**
4. **Our unified supplier API & model** (see `UNIFIED_SUPPLIER_MODEL.md`)

The goal is to show where the **models differ**, what we **abstract**, and what adapter logic is required to support our PoD workflows consistently.

## Quick comparison table

| Dimension | Printify | Printful | Gelato | Our unified supplier API |
|---|---|---|---|---|
| **Protocol** | REST | REST | REST | REST (internal) |
| **Base URLs** | `https://api.printify.com/v1` | `https://api.printful.com` (+`/v2` beta) | Multiple hosts: `api.gelato.com/v3`, `ecommerce.gelatoapis.com/v1`, `order.gelatoapis.com/v4`, `shipment.gelatoapis.com/v1` | `https://{our-backend}/api` |
| **Auth** | PAT or OAuth 2.0 | Private token or OAuth 2.0 | API key (`X-API-KEY`) or OAuth | JWT for our users; supplier credentials stored per connection |
| **Rate limiting** | Documented per-surface (global + catalog + publish) | v1 fixed-ish per minute; v2 leaky bucket headers | `429` documented; exact limits vary | Not explicitly enforced yet (should add) |
| **Pagination** | `page`/`limit` | `offset`/`limit` | `offset`/`limit` | Canonical `cursor` token in adapters |
| **Webhooks** | Supported; HMAC signature header | Supported; v2 adds stronger signature model | Supported; event taxonomy covers orders + store products | We should consume supplier webhooks and normalize to internal events |
| **Catalog primitive** | Blueprint | Catalog product (+ categories + variants) | Product UID (often requires detail calls) | `SupplierCatalogProduct` |
| **Fulfillment/provider selection** | **Required**: blueprint + print provider | Not required for basic catalog pricing | Not required in the same way; country-dependent pricing | `fulfillmentProviders[]` optional, required for Printify quotes |
| **Pricing units** | Often cents (integer) | Often strings/numbers (variant-level) | Country-dependent; shape varies | Always `Money { amount, currency }` |
| **Shipping** | Provider shipping profiles | Shipping rates endpoint (recipient + items) | Shipment service host; country-dependent methods | `quotePricing(...).shipping` (normalized estimate) |
| **Orders** | Shop-scoped orders | Orders + shipments/packages | Orders service host (v4) | `SupplierOrder` |

## Core model differences (what must be abstracted)

### 1) Catalog modeling: “blueprints” vs “products” vs “uids”

- **Printify**
  - Catalog is “Blueprints” (blank templates).
  - You must choose a **Print Provider** to obtain variant availability and pricing.
- **Printful**
  - Catalog is “Products” and “Variants” (variants can be retrieved with product detail calls).
  - Categories are explicit and hierarchical (useful for filtering).
- **Gelato**
  - Catalog products are UID-based and may be returned in minimal form from list endpoints.
  - IDs may appear under different keys across endpoints.

**Our abstraction**: `SupplierCatalogProduct` with a stable `externalId` plus an optional `productTypeKey` for cross-supplier matching.

### 2) Provider selection (Printify-specific)

- Printify pricing requires: `(blueprint_id, print_provider_id)` and often a dedicated variants endpoint.
- Printful/Gelato pricing can be obtained without a separate provider selection (but may be country-specific).

**Our abstraction**:

- `listFulfillmentProviders(productExternalId)` exists, but adapters may return an empty list for suppliers that don’t have this concept.
- `quotePricing` accepts optional `providerExternalId`; Printify adapter requires it (or must pick a deterministic default).

### 3) Pricing and currency normalization

- Printify frequently returns **integer cents**.
- Printful often returns **strings** (or numeric strings) for price/rate.
- Gelato price shapes vary across services and can depend on `country`.

**Our abstraction**:

- All computed costs become `Money { amount, currency }`.
- Adapters must:
  - parse/scale values
  - attach currency
  - preserve raw fields in `supplierData` for auditing

### 4) Shipping modeling differs widely

- **Printify**: shipping profiles per provider and blueprint.
- **Printful**: shipping computed via `/shipping/rates` from recipient+items.
- **Gelato**: shipping methods under a shipment service; usually country-dependent.

**Our abstraction**:

- `quotePricing` optionally includes a “standard shipping” estimate in a normalized shape:
  - first item cost
  - additional item cost

### 5) Orders and fulfillment status semantics differ

Each supplier uses different order state machines and shipment/tracking representation.

**Our abstraction**:

- `SupplierOrderStatus` as a small canonical enum, with supplier-specific details kept in `supplierData`.
- Webhooks are preferred for shipment/tracking state updates.

## Our backend API (current state) — supplier-related surfaces

This is derived from current Flask routes (see `backend/app/blueprints/suppliers/routes.py` and `backend/app/blueprints/products/routes.py`).

### Supplier connections

- `GET /api/suppliers`
- `POST /api/suppliers/<supplier_type>/connect` (API-key based; Printify may require `shop_id`)
- `POST /api/suppliers/connection/<id>/sync`
- `GET /api/suppliers/connection/<id>/products`

### Supplier catalog (UI helper)

- `GET /api/products/user/catalog/<connection_id>`
  - Fetches from DB if synced; otherwise may fetch directly from supplier API.
  - Implements per-supplier category extraction and defensive parsing (notably for Gelato).

### Comparison & switching workflows

- `GET /api/products/compare`
- `GET /api/products/compare/summary`
- `GET /api/products/compare/<product_id>`
- `POST /api/products/switch`

## Key gaps / required adapter behaviors

### Printify-specific gaps

- Need a deterministic strategy for selecting a print provider for comparisons:
  - “default provider” is currently hard-coded in comparison (`print_provider_id = '99'`), which is not robust.
- Publishing is rate-limited separately; bulk publish must respect publish quotas.

### Printful-specific gaps

- Need to standardize whether we connect via:
  - private token (`api_key`) or
  - OAuth (`access_token`/`refresh_token`)
  and make the adapter choose the right credential source consistently.
- v2 beta differs materially (error format, missing/changed resources); keep v1 as default until v2 is stable for our needs.

### Gelato-specific gaps

- Our current `GelatoService` uses `api.gelato.com/v3` for orders and shipping; Gelato docs indicate dedicated service hosts:
  - `order.gelatoapis.com/v4` for orders
  - `shipment.gelatoapis.com/v1` for shipping methods
  The adapter should route calls per service host and version.
- Product IDs are inconsistent across endpoints; always normalize IDs defensively.

## Recommended next step

Implement adapters conforming to `UNIFIED_SUPPLIER_MODEL.md`, then refactor our backend routes so UI consumes supplier data via a single unified contract (catalog → quote → compare → order), while supplier-specific logic stays behind adapters.

