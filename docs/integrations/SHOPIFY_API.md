# Shopify Admin API (Store Integration) — Detailed Notes

This document summarizes Shopify’s **Admin API** from the perspective of our PoD shop-management app: auth, rate limits, webhooks, key objects and the operations we must support.

> Note on “all objects/properties”: Shopify’s Admin API GraphQL schema contains **hundreds of objects and thousands of fields** and changes each version. This doc enumerates the **objects and fields we need for our feature set**, and points to the authoritative schema reference for the exhaustive list.

## API identity

- **Primary interface (recommended)**: GraphQL Admin API
- **Optional / legacy interface**: REST Admin API (Shopify has been steering new public apps to GraphQL; keep REST only for specific resources if needed)
- **GraphQL endpoint**: `https://{shop}.myshopify.com/admin/api/2026-01/graphql.json`
- **Auth**: OAuth (public apps) or Admin access tokens (custom apps)
- **Scopes**: granular (`read_products`, `write_products`, `read_orders`, etc.)

Reference: Shopify GraphQL Admin API reference (`latest`): `https://shopify.dev/docs/api/admin-graphql/latest`.

## Authentication

All GraphQL Admin API requests require a valid access token in:

- `X-Shopify-Access-Token: <token>`

Reference section: “Authentication” in `https://shopify.dev/docs/api/admin-graphql/latest`.

## Error handling (GraphQL-specific)

Shopify GraphQL often returns **HTTP 200** even when an operation “failed” at the application level.

- **Top-level `errors[]`**: query-level failures (including throttling / cost exceeded).
- **`userErrors[]` in mutation payloads**: validation/business errors you must check explicitly.
- **Throttle signals**:
  - `errors[].extensions.code` may include `THROTTLED` / `MAX_COST_EXCEEDED`
  - successful responses include `extensions.cost.throttleStatus` with remaining capacity

Implication: our Shopify adapter must treat “200 + errors” as failure and map it to our internal error shape.

## Rate limits & bulk operations

Shopify uses:

- **GraphQL Admin API**: calculated query cost with a bucket (`requestedQueryCost`, `actualQueryCost`, `throttleStatus` returned in `extensions.cost`).
  - Single query maximum cost is **1000** points.
  - Default restore rates depend on store plan tier.
- **Pagination limit**: arrays are limited to deep pagination of **25,000** objects.
- **Input limit**: arrays in inputs max **250** items.
- **Bulk operations**: recommended for large exports/imports and to bypass max-cost limitations in practice (async).

Reference: `https://shopify.dev/docs/api/usage/rate-limits` and `https://shopify.dev/docs/api/usage/limits`.

## Pagination (GraphQL cursors)

Most Shopify list queries use cursor pagination (`first/after`, `last/before`) and return:

- `pageInfo { hasNextPage, hasPreviousPage, endCursor, startCursor }`
- `edges { cursor, node { ... } }`

Implication: our canonical pagination should use a single `cursor` token (opaque string) and avoid offset-based pagination.

## Webhooks

Shopify supports many webhook topics (orders, products, fulfillments, customers, etc.). Webhooks can be managed:

- via **app configuration file** (recommended for app-wide subscriptions), or
- via **GraphQL** (`webhookSubscriptionCreate`) for shop-specific subscriptions.

Reference: `https://shopify.dev/docs/api/webhooks/latest` and guide `https://shopify.dev/docs/apps/build/webhooks/subscribe/subscribe-using-api`.

### Webhook signature verification (HTTPS delivery)

If we receive webhooks directly over HTTPS (instead of Pub/Sub/EventBridge), we must verify authenticity using the raw request body and Shopify’s shared secret.

Common headers include:

- `X-Shopify-Hmac-Sha256` (signature)
- `X-Shopify-Topic`
- `X-Shopify-Shop-Domain`
- `X-Shopify-Webhook-Id`

Verification is typically HMAC-SHA256 of the raw body using the app secret, base64-encoded, then compared to `X-Shopify-Hmac-Sha256`.

## Core objects (GraphQL) we care about

Below are the Shopify GraphQL objects that map to our features. Field lists are **focused on what we must normalize**.

### Shop

Used for store identity.

- `id` (GID)
- `name`
- `primaryDomain` / domain info
- `currencyCode`
- `timezoneOffset` / locale information (varies by field)

### Product (catalog item)

Represents a product listing container in Shopify’s catalog.

Key fields we use:

- Identity: `id`, `legacyResourceId`
- Merchandising: `title`, `handle`, `vendor`, `productType`, `tags`, `status`
- Content: `description`, `descriptionHtml`
- SEO: `seo { title, description }`
- Media: `featuredMedia`, `media(...)`
- Variants: `variants(...)`, `hasOnlyDefaultVariant`, `totalInventory`, `tracksInventory`
- Publishing: `onlineStoreUrl`, `publishedAt`, resource publications

Reference: `https://shopify.dev/docs/api/admin-graphql/latest/objects/product`.

### ProductVariant (sellable SKU)

Represents a specific variant (size/color) with its own SKU/pricing/inventory linkage.

Key fields we use:

- Identity: `id`, `legacyResourceId`
- Merchandising: `title`, `displayName`, `selectedOptions[]`
- Pricing: `price`, `compareAtPrice`
- SKU/Barcode: `sku`, `barcode`
- Inventory: `inventoryItem { id ... }`, `inventoryQuantity`, `inventoryPolicy`
- Availability: `availableForSale`
- Media: `media(...)`

Reference: `https://shopify.dev/docs/api/admin-graphql/latest/objects/productvariant`.

### InventoryItem / InventoryLevel / Location

Shopify inventory is multi-location and tracked via `InventoryItem` and stock at `InventoryLevel`.

We generally normalize:

- `InventoryItem.id` (GID)
- `Location.id`, name
- Stock quantities by location (sum or primary location depending on our business rules)

### Order (order header)

Shopify’s `Order` is the canonical order header.

Key fields we normalize:

- Identity: `id`, `legacyResourceId`, `name`, `confirmationNumber`
- Status:
  - financial: `displayFinancialStatus`
  - fulfillment: `displayFulfillmentStatus`
  - cancellation: `cancelledAt`, `cancelReason`, `cancellation { ... }`
- Buyer/contact: `customer { ... }`, `email`, `phone`
- Addresses: `shippingAddress`, `billingAddress`
- Amounts (multi-currency “bags”):
  - `totalPriceSet`, `subtotalPriceSet`, `totalTaxSet`, `totalDiscountsSet`, `currentTotalPriceSet`, etc.
- Line items: `lineItems(...)` (connection)
- Fulfillment: `fulfillmentOrders(...)`, `fulfillments(...)`
- Refunds: `refunds(...)`, `refundable`, `suggestedRefund(...)`

Important Shopify constraint: by default only last **60 days** of orders are available unless the app is granted “all orders” access.

Reference: `https://shopify.dev/docs/api/admin-graphql/latest/objects/order`.

### LineItem (order line)

The main mapping for order items.

Key fields:

- Identity: `id`
- Quantity: `quantity`, `fulfillableQuantity`
- Pricing: `originalUnitPriceSet`, discount allocations/applications
- References: `product`, `variant`, `sku` (via variant), `title`
- Properties: custom attributes (for personalization)

### FulfillmentOrder / Fulfillment

Shopify fulfillment is modeled via fulfillment orders (what needs to be shipped) and fulfillments (shipments).

We normalize:

- FulfillmentOrder: id, status, assigned location, line items
- Fulfillment: id, status, tracking info, shipped timestamps

Reference for FulfillmentOrder (example): `https://shopify.dev/docs/api/admin-graphql/latest/objects/fulfillmentorder`.

### Customer / MailingAddress

We treat customer PII carefully; only ingest what’s needed for fulfillment and support.

- Customer: `id`, `email`, name, `tags`
- MailingAddress: name, company, address1/2, city, province, zip, countryCode, phone

### Metafield (custom data)

Metafields are Shopify’s primary extension mechanism.

We use them for:

- linking Shopify resources to our internal IDs (e.g., `pod.manager_template_id`)
- storing SKU mapping and PoD supplier metadata
- storing computed SEO suggestions or applied rules

## Getting the exhaustive object/field list (the “all objects/properties” source of truth)

Because Shopify’s GraphQL schema is the authoritative list of **all objects, fields, input objects, enums, and mutations**, the “complete” inventory is:

- the **Admin GraphQL reference** for a pinned version, e.g. `2026-01`: `https://shopify.dev/docs/api/admin-graphql/latest`
- GraphiQL Explorer: `https://shopify.dev/apps/tools/graphiql-admin-api`
- (Optionally) schema introspection at runtime (via GraphQL introspection queries), which we can cache per version.

## Operations (methods) we need (GraphQL queries/mutations)

Shopify GraphQL is typed; operations are expressed as queries and mutations.

### Store identity / connection

- Query: `shop { name ... }`
- Query: `appInstallation { ... }` (optional)

### Products & variants

- Query: `products(first:, after:, query:)` (catalog sync; supports search syntax)
- Query: `product(id:) { ... variants(...) ... }`
- Mutations:
  - `productCreate`
  - `productUpdate`
  - `productVariantsBulkCreate`
  - `productVariantsBulkUpdate`
  - publish/unpublish via `publishablePublish` (preferred) / legacy product publish APIs

### Inventory

- Query inventory items / levels (depending on app scopes and use-case)
- Mutations for adjustments depend on the current Shopify schema; we will standardize on “adjust inventory quantities” operations behind our adapter layer.

### Orders & fulfillment

- Query: `orders(first:, after:, query:)`
- Query: `order(id:) { ... }`
- Query: `order.fulfillmentOrders(...)`
- Mutations:
  - `orderUpdate` (notes/tags/address updates where allowed)
  - fulfillment-related mutations (create fulfillment / add tracking) via fulfillment orders workflow
  - `refundCreate` for returns/refunds (as needed)

### Webhooks

- Mutation: `webhookSubscriptionCreate(topic:, webhookSubscription:)`
- Optional filters / payload modifications (Shopify supports both)

## Integration implications for PoD

- **Shopify is product+variant centric**: SKU lives primarily on `ProductVariant.sku`.
- **Inventory is multi-location**: we must decide whether to aggregate or choose a “primary” location for reporting and PoD availability checks.
- **Order access is permissioned**: older orders require special scopes/approval; we should design analytics to gracefully degrade if only last 60 days are available.

