# Unified Store Model & Adapter Interfaces (Etsy + Shopify)

This document defines **our canonical object model** and the **adapter interface** layer that lets us operate a mixed fleet of Etsy + Shopify shops using the same UI, workflows, and feature logic.

Goals:

- Present a **single internal model** to the UI + business logic.
- Keep platform-specific quirks behind adapters (Etsy REST vs Shopify GraphQL, status enums, pagination, rate limits).
- Preserve enough platform fields for round-trip edits and debugging (store raw payloads or store “platformRef” blocks).

## Guiding principles

- **Canonical IDs**: Every entity has a stable internal ID. Platform objects are referenced via `platformRef` (platform + external ID).
- **Variant-first SKU tracking**: We treat SKU at `Variant` level. Platforms that don’t support SKUs reliably (Etsy) must still map line items → variant identifiers.
- **Event-driven where possible**: Prefer webhooks (Shopify many topics, Etsy limited) and fallback to polling/sync jobs.
- **Money is structured**: Always store `amount` + `currency`. Never rely on string prices for computation.
- **Extensibility**: Store platform-specific extensions in `platformData` or `metafields`-like structures.

## Canonical entities (TypeScript interfaces)

These interfaces define the minimum “contract” our features need. They are intentionally opinionated and include only normalized fields required by our app. Platform-specific extras belong in `platformData`.

```typescript
export type StorePlatform = 'etsy' | 'shopify'

export type ExternalRef = {
  platform: StorePlatform
  externalId: string // Etsy numeric IDs as string; Shopify GIDs or legacy IDs as string
  externalUrl?: string
}

export type Money = {
  amount: number // decimal stored as number; backend should store as string/Decimal
  currency: string // ISO 4217
}

export type Address = {
  name?: string
  company?: string
  address1?: string
  address2?: string
  city?: string
  province?: string
  zip?: string
  countryCode?: string
  phone?: string
}

export type Customer = {
  id?: string
  email?: string
  firstName?: string
  lastName?: string
  phone?: string
}

export type StoreConnection = {
  id: string
  userId: string
  platform: StorePlatform
  displayName: string
  isConnected: boolean
  isActive: boolean

  // Platform identifiers
  external: ExternalRef

  // OAuth / token metadata (sensitive)
  tokenStatus?: {
    hasAccessToken: boolean
    expiresAt?: string
    hasRefreshToken?: boolean
  }

  lastSyncAt?: string
  connectionError?: string | null
}

export type ListingStatus =
  | 'draft'
  | 'active'
  | 'archived'
  | 'inactive'
  | 'expired'
  | 'unpublished'
  | 'unknown'

export type Variant = {
  id: string
  external: ExternalRef
  sku?: string
  barcode?: string

  title?: string
  options: Array<{ name: string; value: string }>

  price?: Money
  compareAtPrice?: Money

  inventory?: {
    tracked?: boolean
    quantity?: number // aggregated
    byLocation?: Array<{ locationExternalId: string; quantity: number }>
    policy?: 'deny' | 'continue' | 'unknown'
  }

  isAvailableForSale?: boolean

  platformData?: Record<string, unknown>
}

export type Listing = {
  id: string
  external: ExternalRef
  storeConnectionId: string

  status: ListingStatus
  title: string
  description?: string

  tags?: string[]
  materials?: string[]
  productType?: string
  vendor?: string

  seo?: { title?: string; description?: string }

  images?: Array<{ id?: string; url: string; alt?: string }>

  variants: Variant[]

  createdAt?: string
  updatedAt?: string

  platformData?: Record<string, unknown>
}

export type OrderFinancialStatus =
  | 'pending'
  | 'authorized'
  | 'paid'
  | 'partially_paid'
  | 'refunded'
  | 'partially_refunded'
  | 'voided'
  | 'unknown'

export type OrderFulfillmentStatus =
  | 'unfulfilled'
  | 'partial'
  | 'fulfilled'
  | 'in_progress'
  | 'cancelled'
  | 'unknown'

export type OrderLineItem = {
  id: string
  external?: ExternalRef
  title: string
  quantity: number
  sku?: string

  // references
  listingExternalId?: string
  variantExternalId?: string

  unitPrice?: Money
  totalPrice?: Money

  personalization?: Record<string, string> // Etsy personalization / Shopify line item properties

  platformData?: Record<string, unknown>
}

export type Fulfillment = {
  id: string
  external?: ExternalRef
  status:
    | 'pending'
    | 'in_transit'
    | 'delivered'
    | 'cancelled'
    | 'unknown'
  tracking?: {
    number?: string
    url?: string
    carrier?: string
  }
  shippedAt?: string
  deliveredAt?: string
  platformData?: Record<string, unknown>
}

export type Order = {
  id: string
  external: ExternalRef
  storeConnectionId: string

  orderNumber?: string // Etsy receipt id or Shopify #name

  financialStatus: OrderFinancialStatus
  fulfillmentStatus: OrderFulfillmentStatus

  customer?: Customer
  shippingAddress?: Address
  billingAddress?: Address

  currency: string
  totals: {
    subtotal?: Money
    shipping?: Money
    tax?: Money
    discount?: Money
    total: Money
  }

  lineItems: OrderLineItem[]
  fulfillments?: Fulfillment[]

  createdAt?: string
  updatedAt?: string

  platformData?: Record<string, unknown>
}
```

## Adapter interface (platform abstraction)

We implement an adapter per platform (`EtsyAdapter`, `ShopifyAdapter`). Business logic calls the interface; adapters translate to/from Etsy REST / Shopify GraphQL.

```typescript
export type PageCursor = { cursor?: string; hasNextPage?: boolean }

export type ListPage<T> = {
  items: T[]
  next?: PageCursor
  totalEstimate?: number
}

export interface StoreAdapter {
  platform: StorePlatform

  // Connection
  validateConnection(conn: StoreConnection): Promise<{ ok: boolean; error?: string }>
  getStoreIdentity(conn: StoreConnection): Promise<StoreConnection>

  // Listings / catalog
  listListings(
    conn: StoreConnection,
    args: { cursor?: string; query?: string; updatedAfter?: string; pageSize?: number }
  ): Promise<ListPage<Listing>>
  getListing(conn: StoreConnection, listingExternalId: string): Promise<Listing>
  updateListing(
    conn: StoreConnection,
    listingExternalId: string,
    patch: Partial<Pick<Listing, 'title' | 'description' | 'tags' | 'materials' | 'seo'>>
  ): Promise<Listing>

  // Variants / inventory
  updateVariantPrice(
    conn: StoreConnection,
    variantExternalId: string,
    price: Money
  ): Promise<Variant>
  adjustInventory(
    conn: StoreConnection,
    variantExternalId: string,
    adjustment: { locationExternalId?: string; delta?: number; absolute?: number }
  ): Promise<Variant>

  // Orders
  listOrders(
    conn: StoreConnection,
    args: { cursor?: string; createdAfter?: string; statusQuery?: string; pageSize?: number }
  ): Promise<ListPage<Order>>
  getOrder(conn: StoreConnection, orderExternalId: string): Promise<Order>

  // Fulfillment
  createFulfillment(
    conn: StoreConnection,
    orderExternalId: string,
    args: { lineItemExternalIds?: string[]; tracking?: Fulfillment['tracking'] }
  ): Promise<Fulfillment>

  // Webhooks
  listWebhookTopics(): string[]
  // For Etsy: ORDER_PAID only (commercial apps).
  // For Shopify: many topics, configured outside app or via GraphQL.
}
```

### Platform-specific notes (how adapters differ)

- **EtsyAdapter**
  - Uses REST endpoints.
  - Listing variants are accessed via Listing Inventory; SKUs may live there.
  - Webhooks are limited (currently `ORDER_PAID`) and commercial-app-only.
  - “Mark shipped / tracking” support depends on scopes and endpoints.

- **ShopifyAdapter**
  - Uses GraphQL Admin API.
  - Variant SKUs are first-class (`ProductVariant.sku`).
  - Fulfillment uses fulfillment orders; inventory is multi-location.
  - Webhooks cover most resources; can use payload modification + filters.

## Mapping: Etsy vs Shopify → our canonical model

### Listing

- **Etsy Listing** → `Listing`
  - `externalId = listing_id`
  - `variants` from Listing Inventory products/offerings
  - `status` from Etsy listing `state`

- **Shopify Product** → `Listing`
  - `externalId = product GID`
  - `variants` from `Product.variants`
  - `status` from `Product.status` plus publishing state

### Variant / SKU

- **Etsy**: SKU often resides on listing inventory “product” level, not always on listing root.
- **Shopify**: SKU is `ProductVariant.sku`.

### Order

- **Etsy Receipt** → `Order`
  - line items from Transactions
- **Shopify Order** → `Order`
  - line items from LineItem connection
  - fulfillment from FulfillmentOrder + Fulfillment

## Our backend API shape (where these types live)

For implementation, we should expose these canonical objects via backend endpoints like:

- `GET /api/stores` (our `StoreConnection[]`)
- `GET /api/stores/:id/listings`
- `GET /api/stores/:id/orders`

and keep platform-specific endpoints (if needed) under `/api/integrations/{etsy|shopify}/...` but avoid letting UI depend on them.

