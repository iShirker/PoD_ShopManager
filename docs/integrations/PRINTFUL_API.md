# Printful API (PoD Supplier Integration) — Detailed Notes

This document summarizes Printful’s API from the perspective of our PoD ShopManager app: auth, rate limits, pagination, webhooks, key resources (objects), and the operations we need.

> Note on “all objects/properties”: Printful’s API surface is large (and now split across a stable v1 and a v2 beta with different resource shapes and error formats). This doc enumerates the **objects and fields we need for our feature set** (catalog, categories, variants/pricing, shipping rates, stores, orders, files/mockups, webhooks). For exhaustive reference, use Printful’s official docs entrypoint.

## API identity

- **Style**: REST
- **Base URL (v1)**: `https://api.printful.com`
- **Base URL (v2 beta)**: `https://api.printful.com/v2`
- **Auth**: Private tokens or OAuth 2.0 (public apps)
- **Our backend today**: primarily v1 endpoints (see `backend/app/services/suppliers/printful.py`)

## Authentication

Printful supports:

- **Private token** (“API key”): easiest for a single Printful account.
  - Header: `Authorization: Bearer <token>`
- **OAuth 2.0** (Authorization Code): required for multi-user apps.
  - **Authorize URL (used by our backend)**: `https://www.printful.com/oauth/authorize`
  - **Token URL (used by our backend)**: `https://www.printful.com/oauth/token`
  - Header: `Authorization: Bearer <access_token>`

### Store context

Printful has the concept of “stores” in the account. Depending on endpoint and API generation:

- Some flows use a store-id header (documented historically as `X-PF-Store-Id`) to scope actions.
- Other endpoints are explicitly namespaced by store or return store-specific results.

Our integration should treat store selection as a first-class concern.

### Token lifetimes (OAuth)

Historically documented:

- Access tokens: short-lived (e.g., ~1 hour)
- Refresh tokens: longer-lived (e.g., ~90 days)

Our backend already implements refresh behavior in some paths (see `backend/app/blueprints/products/routes.py` token refresh logic).

## Rate limits

Printful enforces per-account rate limits.

- **v1**: commonly documented at ~120 calls/minute (some intensive endpoints lower)
- **v2 beta**: leaky-bucket style with headers such as:
  - `X-Ratelimit-Limit`
  - `X-Ratelimit-Remaining`
  - `X-Ratelimit-Reset`
  - `X-Ratelimit-Policy`

On exceed: `429 Too Many Requests` (often includes `Retry-After`).

## Pagination

Printful list endpoints commonly use:

- `offset`
- `limit`

Design implication: our adapter should normalize pagination to a single `cursor` token for the UI, even if the supplier uses offset.

## Webhooks

Printful supports webhooks for order/shipment/product changes.

### Common v1 event types (examples)

- Orders: `order_created`, `order_updated`, `order_failed`, `order_canceled`, `order_refunded`
- Shipments: `package_shipped`, `package_returned`
- Products: `product_synced`, `product_updated`, `product_deleted`
- Inventory: `stock_updated`
- Holds: `order_put_hold`, `order_put_hold_approval`, `order_remove_hold`

### v2 webhook notes

Printful v2 introduces:

- More granular webhook event taxonomy
- Signature verification via HMAC-SHA256 with dedicated headers
- Expiration dates for webhooks

### Signature verification

Printful documents HMAC verification for webhook deliveries (header names differ by version). Always verify using the **raw body** and the documented shared secret/public key headers.

## Error handling

Expect standard HTTP status codes:

- `400`, `401`, `403`, `404`, `409`, `429`, `5xx`

Notable v2 behavior:

- Printful v2 beta uses RFC 9457 “Problem Details” error bodies (`application/problem+json`).

## Core resources (objects) we care about

### Store

Represents a Printful “store” within an account.

Key fields (typical):

- `id`
- `name`
- optional contact info fields (email/owner_email/contact_email)

Used by our app for: scoping catalog/sync product operations and user selection if multiple stores exist.

### Catalog Product

Printful “catalog products” are blank products available for printing.

Key fields (typical):

- `id`
- `name`
- `type` (production category / method)
- `type_name` (often used as a category label)
- `brand` / manufacturer fields
- media fields (image/images)
- category linkage fields (e.g., `main_category_id`)

### Category

Printful exposes hierarchical categories.

Key fields (typical):

- `id`
- `title` / `name`
- `parent_id`

We often normalize categories into a human-readable path: `Parent > Child > Subchild`.

### Catalog Variant

Sellable variant for a catalog product (size/color, etc.).

Key fields (typical):

- `id`
- `name`
- `size`
- `color`
- `color_code`
- `price` (string/number depending on endpoint)

### Shipping Rate

Computed from:

- `recipient`: `{ country_code, state_code?, city?, zip?, ... }`
- `items`: list of `{ variant_id, quantity }`

Response typically includes a list of shipping methods with:

- `id` (e.g. `STANDARD`)
- `name`
- `rate`
- `currency`

### Sync Product (Ecommerce-linked product)

Printful also supports “sync products” that are linked to an ecommerce platform integration.

Key concepts:

- Sync product: container for variants
- Sync variant: specific SKU/variant that maps to the platform listing variant

Note: In Printful’s v2 beta, some legacy sync-product/template features are not present or differ.

### Order

Represents an order sent to Printful for fulfillment.

Key fields (typical):

- `id`
- `status` lifecycle
- `recipient` / shipping address
- `items[]` (variants + quantities + files/placements)
- shipments/tracking data (often delivered via webhook)

## Operations (methods/endpoints) we need

This section documents our integration contract as operations; each maps to one or more Printful endpoints.

### Connection / identity

- **Get store info**: `GET /store`
- **List stores**: `GET /stores` (commonly used with OAuth)

### Catalog

- **List catalog products**: `GET /products`
- **List categories**: `GET /categories`
- **Get catalog product details**: `GET /products/{product_id}` (commonly returns `{ product, variants }`)
- **Get variant details**: `GET /products/variant/{variant_id}`

### Shipping

- **Get shipping rates**: `POST /shipping/rates`

### Orders

- **Create order**: `POST /orders`
- **Get order**: `GET /orders/{order_id}`
- **Estimate costs**: `POST /orders/estimate-costs`

### Sync products (optional / platform-linked)

- **List sync products**: `GET /sync/products?limit=&offset=`
- **Get sync product**: `GET /sync/products/{sync_product_id}`
- **Create sync product**: `POST /sync/products`

## Integration implications for PoD

- **Catalog vs sync products**: catalog products are “blanks”; sync products are platform-linked. Our unified model must keep these separate.
- **Pagination**: offset/limit requires careful dedupe and stable ordering for long syncs.
- **Category hierarchy**: categories are a tree; store as full paths for UX filtering.
- **Token management**: support both private token and OAuth; refresh tokens can be required for long-lived connections.

## Reference links (starting points)

- **Printful developer docs**: `https://developers.printful.com/docs/`
- **Printful v2 beta docs**: `https://developers.printful.com/docs/v2-beta/`
- **OAuth authorize/token**: `https://www.printful.com/oauth/authorize`, `https://www.printful.com/oauth/token`

