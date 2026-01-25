# Unified Supplier Model & Adapter Interfaces (Printify + Printful + Gelato)

This document defines **our canonical PoD supplier object model** and the **adapter interface** layer that lets us implement supplier-driven workflows (catalog browsing, matching, pricing/shipping comparison, order submission, fulfillment tracking) across Printify, Printful, and Gelato.

Goals:

- Present a **single internal model** to the UI + business logic.
- Hide supplier quirks behind adapters (multi-base URLs, catalog vs shop products, provider selection, pricing units, status enums, pagination).
- Preserve enough supplier fields for round-trip edits and debugging (`supplierData` / raw payloads).

This model complements `UNIFIED_COMMERCE_MODEL.md` (Etsy/Shopify store-side). This doc focuses on **supplier-side** catalog + fulfillment.

## Guiding principles

- **Supplier-neutral IDs**: Every entity has a stable internal ID. Supplier objects are referenced via `external` (`supplier + externalId`).
- **Catalog-first**: Supplier catalog “blank products” are distinct from store-side “listings/products”.
- **Explicit context**: Pricing and shipping depend on:
  - destination country/region
  - chosen fulfillment provider (Printify)
  - variant options (size/color/material)
- **Money is structured**: Always store `amount` + `currency`. Never compute on strings.
- **Keep raw data**: Supplier APIs differ widely; store `supplierData` for debugging and future mapping.

## Canonical entities (TypeScript interfaces)

These interfaces define the minimum contract our supplier-driven features need.

```typescript
export type SupplierPlatform = 'printify' | 'printful' | 'gelato'

export type ExternalRef = {
  supplier: SupplierPlatform
  externalId: string
  externalUrl?: string
}

export type Money = {
  amount: number // decimal stored as number; backend should store as string/Decimal
  currency: string // ISO 4217
}

export type SupplierConnection = {
  id: string
  userId: string
  supplier: SupplierPlatform
  displayName: string
  isConnected: boolean
  isActive: boolean

  // Supplier-specific context IDs
  // - Printify: shopId required for many shop-scoped calls
  // - Gelato: storeId used by ecommerce/store-product surfaces
  supplierContext?: {
    shopId?: string
    storeId?: string
  }

  tokenStatus?: {
    hasApiKey?: boolean
    hasAccessToken?: boolean
    expiresAt?: string
    hasRefreshToken?: boolean
  }

  lastSyncAt?: string
  connectionError?: string | null
}

export type SupplierCatalogProduct = {
  id: string
  external: ExternalRef

  // Canonical “matching key” used for cross-supplier matching:
  // e.g., "gildan 18000", "bella canvas 3001"
  productTypeKey?: string

  name: string
  description?: string
  brand?: string
  model?: string
  category?: string

  images?: Array<{ url: string; alt?: string }>
  thumbnailUrl?: string

  // Fulfillment/provider options (Printify-centric)
  fulfillmentProviders?: SupplierFulfillmentProvider[]

  // Supplier-specific extras
  supplierData?: Record<string, unknown>
}

export type SupplierFulfillmentProvider = {
  id: string
  external: ExternalRef
  name: string
  location?: {
    countryCode?: string
    region?: string
  }
  shippingProfiles?: SupplierShippingProfile[]
  supplierData?: Record<string, unknown>
}

export type SupplierShippingProfile = {
  id?: string
  countries?: string[] // may include "REST_OF_THE_WORLD"
  firstItem?: Money
  additionalItem?: Money
  supplierData?: Record<string, unknown>
}

export type SupplierVariant = {
  id: string
  external: ExternalRef
  productExternalId: string

  // Human-readable
  title?: string
  sku?: string

  // Option selections
  options: Array<{ name: string; value: string }>

  // Availability/pricing are context-dependent
  isAvailable?: boolean

  supplierData?: Record<string, unknown>
}

export type SupplierPricingQuote = {
  productExternalId: string
  providerExternalId?: string // Printify
  country?: string // destination country for country-specific pricing

  currency: string
  baseCost?: Money // “supplier cost” for one unit (where available)
  variantCosts?: Array<{
    variantExternalId: string
    cost?: Money
    supplierData?: Record<string, unknown>
  }>

  // Optional shipping estimate included alongside base cost
  shipping?: {
    methodId?: string
    methodName?: string
    firstItem?: Money
    additionalItem?: Money
  }

  supplierData?: Record<string, unknown>
}

export type SupplierOrderStatus =
  | 'draft'
  | 'created'
  | 'in_production'
  | 'shipped'
  | 'delivered'
  | 'canceled'
  | 'failed'
  | 'unknown'

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
  email?: string
}

export type SupplierOrderLineItem = {
  id: string
  variantExternalId?: string
  productExternalId?: string
  quantity: number

  // For print instructions (placements/files) — supplier-specific today
  printInstructions?: Record<string, unknown>

  supplierData?: Record<string, unknown>
}

export type Shipment = {
  id: string
  status: 'pending' | 'in_transit' | 'delivered' | 'returned' | 'canceled' | 'unknown'
  carrier?: string
  trackingNumber?: string
  trackingUrl?: string
  shippedAt?: string
  deliveredAt?: string
  supplierData?: Record<string, unknown>
}

export type SupplierOrder = {
  id: string
  external: ExternalRef
  supplierConnectionId: string

  status: SupplierOrderStatus

  shipTo: Address
  items: SupplierOrderLineItem[]

  costs?: {
    subtotal?: Money
    shipping?: Money
    tax?: Money
    total?: Money
  }

  shipments?: Shipment[]

  createdAt?: string
  updatedAt?: string

  supplierData?: Record<string, unknown>
}

export type SupplierWebhookEvent = {
  id: string
  supplier: SupplierPlatform
  type: string
  occurredAt?: string
  externalResource?: ExternalRef
  payload: Record<string, unknown>
}
```

## Adapter interface (supplier abstraction)

We implement one adapter per supplier: `PrintifySupplierAdapter`, `PrintfulSupplierAdapter`, `GelatoSupplierAdapter`.

```typescript
export type PageCursor = { cursor?: string; hasNextPage?: boolean }

export type ListPage<T> = {
  items: T[]
  next?: PageCursor
  totalEstimate?: number
}

export interface SupplierAdapter {
  supplier: SupplierPlatform

  // Connection
  validateConnection(conn: SupplierConnection): Promise<{ ok: boolean; error?: string }>
  getAccountIdentity(conn: SupplierConnection): Promise<{
    displayName?: string
    shopId?: string // Printify
    storeId?: string // Gelato / Printful store
  }>

  // Catalog browsing
  listCatalogProducts(
    conn: SupplierConnection,
    args: { cursor?: string; search?: string; category?: string; pageSize?: number }
  ): Promise<ListPage<SupplierCatalogProduct>>
  getCatalogProduct(conn: SupplierConnection, productExternalId: string): Promise<SupplierCatalogProduct>

  // Providers (Printify-centric)
  listFulfillmentProviders(
    conn: SupplierConnection,
    productExternalId: string
  ): Promise<SupplierFulfillmentProvider[]>

  // Variants & pricing
  listVariants(
    conn: SupplierConnection,
    args: { productExternalId: string; providerExternalId?: string; country?: string }
  ): Promise<SupplierVariant[]>

  quotePricing(
    conn: SupplierConnection,
    args: { productExternalId: string; providerExternalId?: string; country?: string }
  ): Promise<SupplierPricingQuote>

  // Orders
  createOrder(conn: SupplierConnection, order: Omit<SupplierOrder, 'id' | 'external'>): Promise<SupplierOrder>
  getOrder(conn: SupplierConnection, orderExternalId: string): Promise<SupplierOrder>
  cancelOrder?(conn: SupplierConnection, orderExternalId: string): Promise<{ ok: boolean }>

  // Webhooks
  listWebhookTopics(): string[]
  verifyWebhookSignature(args: {
    rawBody: string | Uint8Array
    headers: Record<string, string | string[] | undefined>
    secret: string
  }): Promise<{ ok: boolean; error?: string }>
}
```

## Supplier-specific mapping notes

### Printify → canonical model

- `SupplierCatalogProduct` ⇐ Printify **Blueprint**
- `SupplierFulfillmentProvider` ⇐ Printify **Print Provider**
- `SupplierVariant` ⇐ Printify **Variant** (must be fetched per blueprint+provider)
- `quotePricing` must take `providerExternalId` (or choose a default provider deterministically)

### Printful → canonical model

- `SupplierCatalogProduct` ⇐ Printful **Catalog Product**
- Variants come from `GET /products/{id}` as `variants[]`
- Keep “catalog” separate from “sync products” (platform-linked constructs)

### Gelato → canonical model

- `SupplierCatalogProduct` ⇐ Gelato **Product** (UID-based)
- IDs are inconsistent across endpoints; extract from `uid|id|productUid|product_uid`
- Pricing is country-dependent (`/prices?country=`); require `country` input for accurate comparisons
- Treat Gelato as multi-service: route catalog vs orders vs shipping to the appropriate base URL

