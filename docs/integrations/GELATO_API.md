# Gelato API (PoD Supplier Integration) — Detailed Notes

This document summarizes Gelato’s API surfaces from the perspective of our PoD ShopManager app: auth, rate limits, pagination, webhooks, key resources (objects), and the operations we need.

> Note on “all objects/properties”: Gelato’s API is split across multiple services (catalog/ecommerce/orders/shipping) with different base URLs and versions. This doc enumerates the **objects and fields we need for our feature set** (stores, products/catalog, pricing, shipping methods, orders, webhooks). For exhaustive reference, use Gelato’s official docs entrypoints.

## API identity

- **Style**: REST
- **Multiple base URLs (service-oriented)**:
  - **Catalog / products (v3)**: `https://api.gelato.com/v3`
  - **Ecommerce / stores (v1)**: `https://ecommerce.gelatoapis.com/v1`
  - **Orders (v4)**: `https://order.gelatoapis.com/v4`
  - **Shipment methods (v1)**: `https://shipment.gelatoapis.com/v1`
- **Auth**: API key (`X-API-KEY`) and/or OAuth bearer tokens
- **Our backend today**:
  - Uses `https://api.gelato.com/v3` for `products`, `products/{uid}`, `products/{uid}/prices`
  - Uses `https://ecommerce.gelatoapis.com/v1/stores` for stores
  - Uses v3 host for `orders` and `shipping/methods` in `GelatoService` (docs indicate these should be on the dedicated `order.*` and `shipment.*` hosts)

## Authentication

Gelato commonly supports:

- **API key**:
  - Header: `X-API-KEY: <key>`
- **OAuth 2.0** (for public/multi-user integrations):
  - Header: `Authorization: Bearer <access_token>`

Our backend supports both header styles (see `backend/app/services/suppliers/gelato.py`).

## Rate limits

Gelato returns `429 Too Many Requests` when limits are exceeded, but the exact per-second/minute limits can differ by plan and service. Design implications:

- Implement retries with exponential backoff + jitter for transient `5xx`.
- Honor `Retry-After` if present.
- Prefer webhooks for status changes to avoid polling.

## Pagination

Gelato list endpoints commonly use:

- `limit`
- `offset`

Our backend’s catalog syncing code already paginates via offset/limit.

## Webhooks

Gelato supports webhook subscriptions for events such as:

- Orders:
  - `order_status_updated`
  - `order_item_status_updated`
  - `order_item_tracking_code_updated`
  - `order_delivery_estimate_updated`
- Store products / templates:
  - `store_product_created`, `store_product_updated`, `store_product_deleted`
  - `store_product_template_created`, `store_product_template_updated`, `store_product_template_deleted`

### Delivery & retries

- Delivered via HTTP POST.
- Gelato typically retries a limited number of times when non-`2xx` is returned.

### Signature verification

Gelato webhook authentication/signing details can vary by service and doc page; design the adapter so webhook verification is supplier-specific and uses the documented signature headers/secret.

## Error handling

Expect standard HTTP status codes:

- `400`, `401`, `403`, `404`, `409`, `429`, `5xx`

Gelato error bodies can differ across service hosts. Our adapter should normalize to a single internal error shape.

## Core resources (objects) we care about

### Store

Represents a Gelato “store” (ecommerce integration container).

Key fields (typical):

- `id`
- `name` / `title`
- optional contact info fields

Used by our app for: scoping store product templates and filtering catalog context.

### Product (Catalog Product)

Represents a printable blank product in Gelato’s catalog.

Key notes:

- The list endpoint may return **minimal** product records; you often need a detail call to get full metadata.
- Product identifiers can appear under different keys depending on endpoint/version:
  - `uid`, `id`, `productUid`, `product_uid`

Key fields (typical):

- identity: `uid`/`productUid`
- naming: `title`/`name`/`productName`/`displayName`
- classification: `productType`/`productTypeUid` and category-like fields
- media: `imageUrl`/`thumbnailUrl`/`images[]`
- dimensions and printable area metadata (depends on product)

Our sync layer already implements defensive ID extraction across keys (see `backend/app/services/suppliers/sync.py`).

### Product Prices

Pricing is typically country-dependent.

Key fields (typical):

- `price` / base price
- `currency`
- `variants[]` (where available)

Common pattern:

- `GET /products/{product_uid}/prices?country=US`

### Shipping Methods

Shipping methods and pricing can be country-dependent.

Gelato documentation indicates shipping methods live under the shipment service host (`shipment.gelatoapis.com`). Our current service uses a v3 path `shipping/methods`; treat this as an implementation detail to verify and adjust per Gelato’s latest docs.

### Order

Represents an order submitted to Gelato for fulfillment.

Key fields (typical):

- `id`
- status lifecycle
- `items[]` (product/variant + quantity + files/placements)
- `shippingAddress` / recipient info
- costs/taxes/shipping breakdown
- shipments/tracking data (often via webhook)

## Operations (methods/endpoints) we need

This section documents our integration contract as operations.

### Connection / identity

- **List stores**: `GET https://ecommerce.gelatoapis.com/v1/stores`

### Catalog

- **List products**: `GET https://api.gelato.com/v3/products?limit=&offset=&storeId=`
- **Get product**: `GET https://api.gelato.com/v3/products/{product_uid}`
- **Get product prices (by country)**: `GET https://api.gelato.com/v3/products/{product_uid}/prices?country=`

### Shipping

- **Get shipping methods (by country)**:
  - Documented as shipment service (v1): `GET https://shipment.gelatoapis.com/v1/...`
  - Our current backend calls: `GET https://api.gelato.com/v3/shipping/methods?country=`

### Orders

- **Create order**:
  - Documented as order service (v4): `POST https://order.gelatoapis.com/v4/orders`
  - Our current backend calls: `POST https://api.gelato.com/v3/orders`
- **Get order**:
  - Documented: `GET https://order.gelatoapis.com/v4/orders/{id}` (version may vary)
  - Our current backend calls: `GET https://api.gelato.com/v3/orders/{id}`

## Integration implications for PoD

- **Multiple hosts, multiple versions**: treat Gelato as a service mesh; the adapter should route requests per domain (catalog vs orders vs shipments vs ecommerce).
- **Inconsistent IDs**: always normalize product IDs with defensive extraction; store raw payloads for debugging.
- **Country-dependent pricing & shipping**: costs depend on destination; our API should require a `shipToCountry` (or default) to compute comparable costs.
- **Webhooks strongly recommended**: order/shipment events should be consumed via webhooks to reduce polling and improve latency.

## Reference links (starting points)

- Gelato docs portal: `https://dashboard.gelato.com/docs/`
- Webhooks: `https://dashboard.gelato.com/docs/webhooks/`
- Orders (v4): `https://dashboard.gelato.com/docs/orders/v4/create/`
- Shipment methods: `https://dashboard.gelato.com/docs/shipment/methods/`

