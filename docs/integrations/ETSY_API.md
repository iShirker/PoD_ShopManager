# Etsy Open API v3 (Seller Integration) — Detailed Notes

This document summarizes Etsy’s **Open API v3** from the perspective of a PoD shop-management app: auth, rate limits, webhooks, key resources (objects) and the operations we need.

> Note on “all objects/properties”: Etsy’s reference is large and evolves. This doc enumerates **all Etsy objects that matter for our feature set** (shops, listings, inventory/variants, orders/receipts, fulfillment/shipping) with **field-level detail for the fields we must normalize**. For the platform’s complete reference (every endpoint/field), use the official reference entrypoint at `https://developers.etsy.com/documentation/reference`.

## API identity

- **Style**: REST
- **Base URL**: `https://api.etsy.com/v3/application`
- **Auth**: OAuth 2.0 Authorization Code Grant + **PKCE required**
- **Access**:
  - “Personal access” apps (default) can connect up to **5 shops**.
  - “Commercial access” required for general-purpose multi-seller apps (and for webhooks).
  - Source: Etsy Open API v3 docs (“Personal Access” vs “Commercial Access”) and Essentials pages.

## Authentication (OAuth 2.0 + PKCE)

Etsy requires OAuth 2.0 Authorization Code Grant and PKCE.

- **Authorization endpoint**: `https://www.etsy.com/oauth/connect`
- **Token endpoint**: `https://api.etsy.com/v3/public/oauth/token`
- **Access token lifetime**: ~1 hour (`expires_in: 3600`)
- **Refresh token lifetime**: ~90 days (per docs)
- **Scopes**: space-separated list. Examples include:
  - `shops_r`, `shops_w`
  - `listings_r`, `listings_w`, `listings_d`
  - `transactions_r`, `transactions_w`
  - `profile_r`, `email_r`

Reference: Etsy “Authentication” essentials: `https://developers.etsy.com/documentation/essentials/authentication`.

### Required request headers (typical)

Etsy uses bearer tokens. In practice you’ll send:

- **Authorization**: `Bearer <oauth_access_token>`
- **x-api-key**: `<etsy_app_keystring>` (depending on endpoint/auth type; Etsy v3 commonly uses app key + bearer token)

## Rate limits

Etsy rate limits are application-based with two controls:

- **QPS** (queries per second)
- **QPD** (queries per day) using a sliding 24-hour window

Responses include headers like:

- `x-limit-per-second`, `x-remaining-this-secon`
- `x-limit-per-day`, `x-remaining-today`

On exceed, Etsy responds `429` with `retry-after`.

Reference: `https://developers.etsy.com/documentation/essentials/rate-limits/`.

## Pagination (list endpoints)

Etsy list endpoints are REST-style and typically support some combination of:

- `limit` (page size)
- `offset` (start index)
- and/or time filters (e.g., “updated since”) depending on resource

Because the specific pagination parameters vary by resource, treat pagination as **resource-defined** and implement it behind the Etsy adapter.

## Webhooks

Etsy webhooks are currently **commercial-app-only** and (as of the doc snapshot) support:

- `ORDER_PAID`

Payload includes `event_type`, `event_id`, `created_at`, and `data` with `resource_url` pointing to the receipt.

Signature verification uses headers:

- `webhook-id`
- `webhook-timestamp`
- `webhook-signature`

Reference: `https://developers.etsy.com/documentation/essentials/webhooks`.

## Error handling (common patterns)

- **HTTP 401/403**: invalid/expired token or missing scopes.
- **HTTP 404**: resource not found (or not visible to the authenticated seller).
- **HTTP 429**: rate limit exceeded (`retry-after` header).
- **HTTP 5xx**: transient Etsy errors; use retries with exponential backoff.

## Core resources (objects) we care about

Below are the Etsy objects we must support for our features. Etsy returns JSON; names can vary slightly by endpoint. We normalize these into our internal model (see `UNIFIED_COMMERCE_MODEL.md`).

### Shop

Represents a seller storefront.

- **Identity**
  - `shop_id` (number/string)
  - `shop_name` (string)
  - `url` (string, optional)
- **Operational**
  - `created_timestamp` / `created_at`
  - `is_vacation` / `vacation_mode`
  - `currency_code` (primary currency)
  - `language` / locale (if available)
- **Stats we may store**
  - listing counts, sales counts, etc. (not always available for all app types/scopes)

Used by our app for: connect store, show store info, scope listing/order sync.

### Listing (product listing)

Etsy’s “Listing” is the public catalog item in the shop.

Typical fields we care about:

- **Identity & state**
  - `listing_id`
  - `state` (draft/active/inactive/expired/etc)
  - `is_digital`, `is_supply` (if present)
  - `type` (physical/digital)
- **Content**
  - `title`
  - `description` (HTML/markdown-ish; may contain HTML)
  - `tags[]`
  - `materials[]`
  - `taxonomy_id` / category
  - `shipping_profile_id` / `processing_profile_id` (if available)
- **Merchandising**
  - `quantity` (if single-SKU listing)
  - `price` (often a money object or amount+currency)
  - `currency_code`
  - `sku` (may be per-variation; sometimes missing at listing root)
- **Media**
  - images are usually separate resources; listing endpoints may provide `image_ids[]` or embedded images depending on endpoint.
- **Timestamps**
  - `created_timestamp` / `created_at`
  - `updated_timestamp` / `updated_at`

Used by our app for: listing sync, SKU tracking, title/description editing, SEO (tags/title), image sync, availability status, mapping to PoD template.

### ListingInventory (variants/options)

Etsy’s variant system is modeled on **inventory products** and **offerings**. The “Listing Inventory” resource is where we reliably get size/color style variants.

Key concepts:

- **Product** (within listing inventory): a variant definition (option values)
  - `product_id`
  - `sku` (often per product)
  - `property_values[]`: option selections
    - `property_id` (option definition)
    - `property_name` (human-readable)
    - `values[]` (value strings)
    - `value_ids[]` (if provided)
- **Offering**: sellable offer with price/quantity for the variant
  - `offering_id`
  - `price` (amount + currency)
  - `quantity`
  - `is_enabled`

Reference entrypoint: `https://www.etsy.com/developers/documentation/reference/listinginventory`.

Used by our app for: variant SKUs, per-variant price rules, per-variant stock (where applicable), syncing to our `UnifiedVariant`.

### Receipt (order header)

Etsy’s “Receipt” is the canonical order header for sellers.

Fields we normalize:

- **Identity**
  - `receipt_id`
  - `shop_id`
- **Status**
  - paid / payment status (varies; sometimes boolean flags)
  - shipped status (varies; sometimes boolean flags)
  - cancellation/refund states (if present)
- **Buyer**
  - buyer user id (if available)
  - `name` / `buyer_name`
  - `email` (requires special access for some apps/fields)
- **Amounts**
  - `total_price` / `grandtotal` (money)
  - `subtotal`, `shipping_cost`, `tax_cost`, `discount_amount` (where available)
  - `currency_code`
- **Addresses**
  - shipping address fields: `first_line`, `second_line`, `city`, `state`, `zip`, `country_iso`, `phone`
- **Timestamps**
  - created / paid / shipped timestamps (as available)

Used by our app for: orders dashboard, fulfillment queue, profitability calculations.

### Transaction (order line item)

Etsy’s “Transaction” corresponds closely to an order line item.

Key fields:

- **Identity**
  - `transaction_id`
  - `receipt_id`
  - `listing_id`
- **Merchandising**
  - `title`
  - `quantity`
  - `price` (money)
  - `sku` (if present; critical for SKU-level tracking)
  - `variations` / selected options (if present)
  - `personalization` (if enabled on listing)
- **Fulfillment**
  - shipping profile / processing time fields can be inferred from listing, not always on transaction.

Reference entrypoint: `https://www.etsy.com/developers/documentation/reference/transaction`.

Used by our app for: SKU tracking, mapping to our internal product/template, sending to PoD supplier for fulfillment.

### Shipping / fulfillment resources (Etsy side)

Etsy has shipping profiles and fulfillment guidance, but capabilities vary by app type and endpoint availability. For our integration, we treat these as **optional**, and focus on:

- Reading enough fields to **display** shipping/processing choices.
- Avoid blocking order ingestion if shipping objects are missing.

See Etsy’s “Fulfillment tutorial” and “Shop management tutorial” in the docs navigation.

## Reference links (starting points)

Some Etsy v3 reference pages are stable and linkable directly (useful for implementers):

- **Docs home**: `https://developers.etsy.com/documentation/`
- **Auth**: `https://developers.etsy.com/documentation/essentials/authentication`
- **Rate limits**: `https://developers.etsy.com/documentation/essentials/rate-limits/`
- **Webhooks**: `https://developers.etsy.com/documentation/essentials/webhooks`
- **Listing inventory**: `https://www.etsy.com/developers/documentation/reference/listinginventory`
- **Transaction**: `https://www.etsy.com/developers/documentation/reference/transaction`

## Operations (methods/endpoints) we typically need

Because Etsy’s full endpoint list is large (and the web reference is dynamic), we document **our integration contract** as a set of operations; each operation maps to one or more Etsy endpoints.

### Identity / shop discovery

- **Get shops for token**: used after OAuth connect to enumerate shops for a user.
  - Required scopes typically include `shops_r`.

### Listings

- **List listings** for a shop (paged)
- **Get listing** by id
- **Update listing** content (title/description/tags)
  - Requires `listings_w`
- **Read listing inventory** (variants) and update variants/inventory where allowed

### Orders

- **List receipts** (orders) for a shop (paged; filters by date/status)
  - Requires `transactions_r`
- **Get receipt** details
- **List transactions** for a receipt (line items)
- **Mark shipped / add tracking** (capability varies; may require `transactions_w`)

### Webhooks (optional but preferred)

- Subscribe to `ORDER_PAID` webhook (commercial apps only)
- Verify signatures; de-dupe by `webhook-id`

## Integration implications for PoD

- **Etsy is listing-centric**: our unified model should treat Etsy Listing as `UnifiedListing` with optional variants via listing inventory.
- **SKU availability is inconsistent**: Etsy SKUs can exist at listing-inventory product level; we must map SKU at **variant** granularity where possible.
- **Order entrypoint is Receipt/Transaction**: we should treat Receipt as `UnifiedOrder` and Transactions as `UnifiedOrderLineItem`.

