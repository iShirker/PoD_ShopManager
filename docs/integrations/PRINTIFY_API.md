# Printify API (PoD Supplier Integration) — Detailed Notes

This document summarizes Printify’s API from the perspective of our PoD ShopManager app: auth, rate limits, pagination, webhooks, the key resources (objects) we must normalize, and the operations we need.

> Note on “all objects/properties”: Printify’s reference is large and evolves (and Printify also has a newer “v2” JSON:API surface). This doc enumerates the **Printify objects and fields that matter for our feature set** (catalog/blueprints, print providers, variants/pricing, shipping profiles, shop products, orders, uploads, webhooks). For exhaustive reference, start from Printify’s official documentation entrypoint.

## API identity

- **Style**: REST
- **Primary API version used by our backend today**: v1
- **Base URL (v1)**: `https://api.printify.com/v1`
- **Auth**: Personal Access Token (PAT) *or* OAuth 2.0
- **Request content type**: `application/json`

## Authentication

Printify supports:

- **Personal Access Token (PAT)**: simplest for a single Printify account.
  - **Header**: `Authorization: Bearer <token>`
  - Typical for server-to-server integrations or “private” tooling.
- **OAuth 2.0 (Authorization Code)**: required for multi-user/public apps.
  - **Authorize URL (used by our backend)**: `https://printify.com/oauth/authorize`
  - **Token URL (used by our backend)**: `https://printify.com/oauth/token`
  - **Headers**: `Authorization: Bearer <access_token>`

### Scopes (OAuth)

Printify OAuth uses granular scopes. Commonly relevant scopes for our PoD feature set include (names may vary by doc version):

- Shops: `shops.read`
- Catalog: `print_providers.read`
- Products: `products.read`, `products.write`
- Orders: `orders.read`, `orders.write`
- Uploads: `uploads.read`, `uploads.write`
- Webhooks: `webhooks.read`, `webhooks.write`

### Token lifetimes (OAuth)

Printify token lifetimes are documented and can change; historically:

- **Access tokens** are short-lived (hours).
- **Refresh tokens** are longer-lived (weeks/months).

Our app should treat access tokens as expiring and refresh when needed.

## Rate limits

Printify enforces rate limits per API surface. Commonly documented limits include:

- **Global API**: ~600 requests/minute
- **Catalog API**: ~100 requests/minute
- **Publishing**: ~200 publish requests / 30 minutes

On exceed: `429 Too Many Requests` (honor `Retry-After` when provided).

## Pagination

Printify v1 list endpoints commonly use:

- `page` (1-based)
- `limit`

Responses often include pagination metadata such as:

- `current_page`, `last_page`, `total`, `per_page`, `from`, `to`

## Webhooks

Printify supports webhook subscriptions for shop/account events.

### Delivery & retries

- Webhooks are delivered via HTTP POST to your endpoint.
- Retry policy is typically limited (e.g., a few retries) and requires a successful `2xx` response.

### Signature verification

Printify provides an HMAC signature header (commonly documented as `X-Pfy-Signature`). Verify with:

- **Algorithm**: HMAC-SHA256 over the raw request body
- **Secret**: configured webhook secret (from Printify webhook settings)
- **Compare**: computed signature vs header value

### Common event types (examples)

Event names evolve, but commonly include:

- Shop/account: `shop:disconnected`
- Product lifecycle: `product:deleted`, `product:publish:started`
- Order lifecycle: `order:created`, `order:updated`, `order:sent-to-production`
- Shipping: `order:shipment:created`, `order:shipment:delivered`

## Error handling

Expect standard HTTP status codes:

- **400**: validation error
- **401**: invalid/expired token
- **403**: missing permission
- **404**: resource not found (also seen when an endpoint path differs, e.g. `shops.json` vs `shops`)
- **409**: conflict (resource state)
- **429**: rate limited
- **5xx**: transient provider errors

Our backend should:

- Retry transient `5xx` with exponential backoff.
- Respect `Retry-After` for `429`.
- Preserve the response body for debugging (but avoid logging tokens).

## Core resources (objects) we care about

Below are the Printify concepts we normalize for our app.

### Shop

Represents a Printify “shop” (usually tied to an ecommerce channel connection).

Key fields (commonly present):

- `id` (number/string)
- `title` (string)
- `sales_channel` / channel metadata (string/object)
- timestamps (created/updated)

Used by our app for: scoping API calls (products/orders are under a shop), and user selection when multiple shops exist.

### Blueprint (Catalog Product)

Blueprints are Printify’s **blank product templates** (catalog).

Key fields:

- `id`
- `title`
- `description`
- `brand`
- `model`
- `category`
- `images[]` (URLs/objects)

Used by our app for: supplier catalog browsing, matching product types across suppliers, and building provider+variant availability.

### Print Provider

Printify fulfills via third-party print providers. Availability/pricing varies by provider.

Key fields:

- `id`
- `title` / `name`
- `location` / region metadata
- supported variants

Used by our app for: selecting the cheapest/fastest provider and for pricing/shipping computation.

### Variant

Sellable configuration (e.g., size/color). In Printify, variants are usually fetched per **blueprint + print provider**.

Key fields (typical):

- `id`
- option values (size/color/etc; depends on blueprint)
- `price` (integer, often **in cents**)
- `is_enabled` / availability flags

### Shipping Profile / Rates

Shipping is provider/blueprint-dependent.

Key fields (typical):

- `profiles[]`
  - `countries[]` (including `REST_OF_THE_WORLD`)
  - `first_item { cost, currency }`
  - `additional_items { cost, currency }`

### Shop Product

Products under a Printify shop (may be mapped to an ecommerce listing).

Key fields (typical):

- `id`
- `title`, `description`
- `blueprint_id`
- `print_provider_id`
- `variants[]` (enabled variants + pricing overrides)
- `images[]`, `tags[]`
- publishing status / sync status (varies)

### Order

Represents a fulfillment order sent to Printify.

Key fields (typical):

- `id`
- `address_to` (shipping address)
- `line_items[]` (variant + quantity + print instructions)
- status lifecycle fields (created → in production → shipped, etc.)
- shipping/tracking info (may arrive via webhook)

### Upload

Artwork/images uploaded to Printify for printing.

Key fields (typical):

- `id`
- file URL(s)
- status fields (processing/ready)

## Operations (methods/endpoints) we need

This section describes the operations our integration must support; each maps to one or more Printify endpoints.

### Connection / identity

- **List shops**: `GET /shops.json` (fallback `GET /shops`)
- **Get shop**: `GET /shops/{shop_id}.json`

> Our backend already implements the `.json` fallback behavior (see `backend/app/services/suppliers/printify.py`).

### Catalog (blueprints, providers, variants, shipping)

- **List blueprints**: `GET /catalog/blueprints.json`
- **Get blueprint**: `GET /catalog/blueprints/{blueprint_id}.json`
- **List blueprint providers**: `GET /catalog/blueprints/{blueprint_id}/print_providers.json`
- **List provider variants**: `GET /catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/variants.json`
- **Get provider shipping**: `GET /catalog/blueprints/{blueprint_id}/print_providers/{print_provider_id}/shipping.json`

### Shop products

- **List shop products**: `GET /shops/{shop_id}/products.json?page=&limit=`
- **Get shop product**: `GET /shops/{shop_id}/products/{product_id}.json`
- **Create shop product**: `POST /shops/{shop_id}/products.json`
- **Publish shop product**: `POST /shops/{shop_id}/products/{product_id}/publish.json`

### Orders

- **Create order**: `POST /shops/{shop_id}/orders.json`
- (Common additional operations): list/get orders, cancel orders (depending on Printify’s current API surface)

## Integration implications for PoD

- **Provider-dependent pricing**: you cannot compute cost from blueprint alone; you must choose a print provider and fetch provider variants.
- **Currency scaling**: many pricing values are integers in cents; normalize to our `Money` type.
- **Shipping is a separate call**: shipping costs come from a provider shipping profile; don’t assume a fixed rate.
- **Webhooks strongly recommended**: use webhooks for order shipment status/tracking to avoid expensive polling.

## Reference links (starting points)

- **Printify Developers portal**: `https://developers.printify.com/`
- **Printify API base (v1)**: `https://api.printify.com/v1`
- **OAuth authorize/token**: `https://printify.com/oauth/authorize`, `https://printify.com/oauth/token`

