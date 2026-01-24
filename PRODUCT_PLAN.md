# PoD Shop Manager - Product Plan & Development Roadmap

## Executive Summary

This document outlines the product evaluation, feature prioritization, and comprehensive development plan for a Print-on-Demand (PoD) management platform that integrates Etsy, Shopify, and PoD suppliers (Gelato, Printify, Printful).

**Related documents:**
- **[SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md)** – Three tiers (Starter $19.99, Growth $49.99, Scale $99.99), free trial, limits, overages.
- **[COMPETITOR_ANALYSIS.md](./COMPETITOR_ANALYSIS.md)** – Competitors by feature, pricing, financials, differentiation.
- **[FEATURE_PRIORITY.md](./FEATURE_PRIORITY.md)** – Feature–plan mapping and MVP scope.

---

## Clarifications Applied (2025-01-23)

### Target Users
- **Primary**: New PoD sellers (onboard first), then growing/established.
- **Audience**: Solo sellers only (no teams initially).
- **Revenue range**: $0 (fresh start) to $10,000+/month.
- **Plans**: Three subscription tiers + limited-time free trial; see [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md).

### Pricing Model
- **Subscription**: Yes. **$19.99 – $99.99/month** (Starter / Growth / Scale).
- **Per-transaction fees**: Only when the app incurs extra cost (e.g. AI usage, storage overage, mockup overage). Otherwise subscription-only.

### Technical Constraints
- **Mockup generation**: Build **our own** mockup/preview system. Design our API to mirror competitor structures (e.g. Customily, Dynamic Mockups) so we can swap or add third-party integrations later. No external mockup API dependency for initial launch.
- **Hosting**: **Railway** for now. See **Part 7.5** for three alternatives (Render, Fly.io, AWS) and comparison.
- **Team**: 1 person + AI initially; may grow by 1–2 later.

### Success Metrics
- **Month 1 (public launch)**: 100 users → **$2,000/month** subscription revenue.
- **Year 1**: 1,000 users → **$20,000/month** subscription revenue.
- **Revenue targets**: Year 1 **$100,000** | Year 2 **$500,000** | Year 3 **$1,000,000**.
- **Differentiation**: See [COMPETITOR_ANALYSIS.md](./COMPETITOR_ANALYSIS.md) for competitor comparison and PoD Shop Manager positioning.

---

## Part 1: Feature Evaluation & Prioritization

### Your Proposed Features - Evaluation

#### 1. Multi-Product Listing Management with SKU Tracking ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: PoD sellers struggle with inventory sync across platforms. One product variation (e.g., "White T-Shirt, Size M, Design A") needs to map correctly to supplier SKUs.
- **Market Need**: Research shows SKU mismatches cause overselling, fulfillment delays, and manual errors.
- **Competitive Advantage**: Most tools handle single-product listings. Multi-product variant management is a differentiator.

**Implementation Complexity**: Medium-High
**Business Value**: Very High

**Recommendations:**
- Support variant-level SKU mapping (Size × Color × Design × Customization)
- Real-time inventory sync across Etsy/Shopify
- Automatic SKU generation with customizable templates
- Bulk SKU import/export

---

#### 2. Real-Time Product Customization with Mockup Preview ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: Customers want to see customizations before ordering. Current solutions require post-purchase personalization links.
- **Market Need**: Tools like Customily and Dynamic Mockups exist but are expensive ($20-50/month). Integrated solution is valuable.
- **Competitive Advantage**: Real-time preview increases conversion rates by 20-30% according to industry data.

**Implementation Complexity**: High (requires image processing, mockup generation API)
**Business Value**: Very High

**Recommendations:**
- **Own mockup implementation**: No third-party mockup API at launch. Use in-house image processing (e.g. Pillow, canvas compositing). Design our API to match competitor patterns (templates, placements, text/image layers) for future integrations.
- Support text, images, clipart, maps customization
- Generate production-ready files automatically
- Store customer customization data for order fulfillment

---

#### 3. Price Development & Profitability Calculator ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: PoD sellers lose money due to miscalculated fees. Etsy fees can be 6.5-25% total, Shopify has transaction fees.
- **Market Need**: Existing calculators (EverBee, EtsyProfitCalculator) are standalone tools. Integrated solution saves time.
- **Competitive Advantage**: Real-time profitability analysis prevents losses.

**Implementation Complexity**: Medium
**Business Value**: Very High

**Recommendations:**
- Real-time fee calculation (Etsy: listing, transaction, payment processing, ads; Shopify: transaction, payment processing)
- Support for multiple fee tiers (Etsy Offsite Ads: 15% <$10k, 12% >$10k)
- Minimum profitable price calculator
- Margin analysis dashboard
- Historical profitability tracking

---

#### 4. Automatic Discount System with Scheduling ⭐⭐⭐⭐
**Seller Interest: HIGH**

**Why it's valuable:**
- **Pain Point**: Manual discount management is time-consuming. Sellers want to schedule seasonal sales, flash sales, etc.
- **Market Need**: Shopify has native scheduling; Etsy requires manual creation. Automation saves hours per week.
- **Competitive Advantage**: Prevents unprofitable discounts through margin checks.

**Implementation Complexity**: Medium
**Business Value**: High

**Recommendations:**
- Discount program templates (Holiday Sales, Flash Sales, BOGO)
- Automatic margin validation before applying discounts
- Multi-platform sync (create on Etsy + Shopify simultaneously)
- Performance analytics (revenue impact, conversion lift)
- Restart/recurring discount support

---

### Additional Features PoD Sellers Request (Based on Research)

#### 5. SEO Optimization Assistant ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: #1 reason PoD shops fail is poor SEO. Sellers don't optimize titles (140 chars), tags (13 available), descriptions.
- **Market Need**: Tools like AnywherePOD offer SEO helpers, but integrated solution is better.

**Features:**
- Keyword research integration
- Title optimization (use all 140 characters)
- Tag suggestions (all 13 Etsy tags)
- Description templates with SEO best practices
- Competitor analysis

---

#### 6. Bulk Listing Creation & Management ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: Creating 100+ listings manually takes days. PoD sellers need to scale quickly.
- **Market Need**: AnywherePOD offers this, but integration with your SKU system is unique.

**Features:**
- CSV/Excel import for bulk listing creation
- Template-based listing generation
- Bulk image upload with automatic mockup generation
- Bulk price updates
- Bulk inventory sync

---

#### 7. Order Fulfillment Automation ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: Manual order processing is error-prone. Sellers need automatic routing to PoD suppliers.
- **Market Need**: Persify processes 5,000+ orders/day automatically. This is a core feature.

**Features:**
- Automatic order routing to correct PoD supplier based on SKU
- Customization data extraction from Etsy/Shopify
- Automatic fulfillment API calls to suppliers
- Order status tracking and sync
- Shipping label generation

---

#### 8. Multi-Store Management Dashboard ⭐⭐⭐⭐
**Seller Interest: HIGH**

**Why it's valuable:**
- **Pain Point**: Managing multiple Etsy shops and Shopify stores is overwhelming.
- **Market Need**: Successful sellers use both platforms. Unified dashboard is essential.

**Features:**
- Unified inventory view across all stores
- Cross-platform analytics
- Centralized order management
- Store performance comparison

---

#### 9. Design Library & Asset Management ⭐⭐⭐⭐
**Seller Interest: HIGH**

**Why it's valuable:**
- **Pain Point**: Managing hundreds of designs across products is chaotic.
- **Market Need**: Integration with Canva, design storage, version control.

**Features:**
- Cloud storage for designs
- Design-to-product mapping
- Version control
- Canva integration (1-click import)
- Design performance analytics (which designs sell best)

---

#### 10. Analytics & Reporting ⭐⭐⭐⭐
**Seller Interest: HIGH**

**Why it's valuable:**
- **Pain Point**: Sellers need to understand what's working (products, designs, pricing).
- **Market Need**: Etsy/Shopify analytics are basic. Advanced insights drive growth.

**Features:**
- Product performance (best sellers, worst performers)
- Design performance analysis
- Profitability by product/category
- Sales trends and forecasting
- Customer behavior insights

---

#### 11. Automated Inventory Sync ⭐⭐⭐⭐⭐
**Seller Interest: VERY HIGH**

**Why it's critical:**
- **Pain Point**: Overselling when inventory sells on one platform but not updated on others.
- **Market Need**: Research shows this is a top pain point. Real-time sync prevents losses.

**Features:**
- Real-time inventory updates across Etsy/Shopify
- Low stock alerts
- Automatic listing deactivation when out of stock
- Supplier inventory sync (if suppliers provide API)

---

#### 12. Tax & Compliance Management ⭐⭐⭐
**Seller Interest: MEDIUM-HIGH**

**Why it's valuable:**
- **Pain Point**: Tax calculations, VAT, compliance across regions.
- **Market Need**: Important for international sellers.

**Features:**
- Tax calculation by region
- VAT handling
- Compliance reporting
- Sales tax collection automation

---

## Part 2: Feature Prioritization Matrix

### Phase 1: MVP (Months 1-3) - Core Functionality
1. ✅ Multi-Product Listing Management with SKU Tracking
2. ✅ Price Development & Profitability Calculator
3. ✅ Automated Inventory Sync
4. ✅ Order Fulfillment Automation (basic)
5. ✅ Multi-Store Management Dashboard

### Phase 2: Growth Features (Months 4-6)
6. ✅ Real-Time Product Customization with Mockup Preview
7. ✅ Bulk Listing Creation & Management
8. ✅ SEO Optimization Assistant
9. ✅ Automatic Discount System with Scheduling

### Phase 3: Advanced Features (Months 7-9)
10. ✅ Design Library & Asset Management
11. ✅ Advanced Analytics & Reporting
12. ✅ Tax & Compliance Management

---

## Part 3: Detailed App Architecture

### 3.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/TypeScript)               │
│  - Dashboard, Product Management, Analytics, Settings       │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              Backend API (Flask/Python)                      │
│  - REST API, Authentication, Business Logic                  │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                     │
│  - Products, Orders, Listings, Discounts, Analytics          │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│              External Integrations Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Etsy API │  │Shopify   │  │ Gelato   │  │Printify │    │
│  │           │  │  API     │  │   API    │  │   API   │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│  ┌──────────┐  ┌──────────┐                               │
│  │Printful  │  │ Mockup    │                               │
│  │   API    │  │   API     │                               │
│  └──────────┘  └──────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Core Modules

#### Module 1: Product Management
- **Product Catalog**: Base products from PoD suppliers
- **Variant Management**: Size, Color, Design combinations
- **SKU Generation**: Automatic SKU creation with templates
- **Product Mapping**: Link Etsy/Shopify variants to PoD supplier products

#### Module 2: Listing Management
- **Listing Creation**: Single and bulk listing creation
- **Listing Sync**: Sync inventory, prices, descriptions
- **Listing Templates**: Reusable templates for quick creation
- **SEO Optimization**: Title, tags, description optimization

#### Module 3: Order Management
- **Order Processing**: Receive orders from Etsy/Shopify
- **Fulfillment Routing**: Route to correct PoD supplier
- **Customization Extraction**: Parse customer customization data
- **Order Tracking**: Track fulfillment status

#### Module 4: Pricing & Profitability
- **Fee Calculator**: Calculate all platform fees
- **Profitability Analysis**: Real-time margin calculation
- **Price Optimization**: Suggest optimal pricing
- **Discount Validation**: Ensure discounts remain profitable

#### Module 5: Discount Management
- **Discount Programs**: Create and manage discount campaigns
- **Scheduling**: Schedule start/end times
- **Platform Sync**: Create discounts on Etsy/Shopify
- **Performance Analytics**: Track discount effectiveness

#### Module 6: Customization & Mockups
- **Customization Engine**: Handle text, images, clipart
- **Mockup Generation**: Real-time preview generation
- **Production Files**: Generate print-ready files
- **Customer Preview**: Show customers their customizations

#### Module 7: Analytics & Reporting
- **Sales Analytics**: Revenue, orders, trends
- **Product Performance**: Best/worst sellers
- **Profitability Reports**: Margin analysis
- **Forecasting**: Sales predictions

---

## Part 4: Database Schema

### Core Tables

#### 4.1 Products & Variants

```sql
-- Base products from PoD suppliers
CREATE TABLE supplier_products (
    id SERIAL PRIMARY KEY,
    supplier_type VARCHAR(50) NOT NULL, -- 'gelato', 'printify', 'printful'
    supplier_product_id VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    product_type VARCHAR(255),
    brand VARCHAR(255),
    model VARCHAR(255),
    category VARCHAR(255),
    base_price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    available_sizes TEXT[], -- Array of sizes
    available_colors JSONB, -- Array of color objects
    thumbnail_url TEXT,
    images TEXT[],
    supplier_connection_id INTEGER REFERENCES supplier_connections(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(supplier_connection_id, supplier_product_id)
);

-- Product variants (combinations of size, color, design)
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    supplier_product_id INTEGER REFERENCES supplier_products(id),
    size VARCHAR(50),
    color VARCHAR(100),
    color_hex VARCHAR(7),
    sku VARCHAR(255) UNIQUE NOT NULL,
    supplier_variant_id VARCHAR(255), -- Variant ID from supplier
    base_price DECIMAL(10,2),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Designs (customer designs/images)
CREATE TABLE designs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    design_type VARCHAR(50), -- 'image', 'text', 'clipart'
    file_url TEXT,
    thumbnail_url TEXT,
    metadata JSONB, -- Additional design data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Product-Design mappings (which designs can go on which products)
CREATE TABLE product_design_mappings (
    id SERIAL PRIMARY KEY,
    supplier_product_id INTEGER REFERENCES supplier_products(id),
    design_id INTEGER REFERENCES designs(id),
    placement VARCHAR(50), -- 'front', 'back', 'sleeve', etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.2 Etsy/Shopify Listings

```sql
-- Etsy listings
CREATE TABLE etsy_listings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    etsy_shop_id INTEGER REFERENCES etsy_shops(id),
    etsy_listing_id VARCHAR(255) UNIQUE, -- Etsy's listing ID
    title VARCHAR(140) NOT NULL, -- Etsy limit
    description TEXT,
    tags TEXT[], -- Up to 13 tags
    price DECIMAL(10,2),
    quantity INTEGER DEFAULT 0,
    state VARCHAR(50), -- 'active', 'draft', 'inactive'
    seo_score INTEGER, -- Calculated SEO optimization score
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Etsy listing variants (maps to product_variants)
CREATE TABLE etsy_listing_variants (
    id SERIAL PRIMARY KEY,
    etsy_listing_id INTEGER REFERENCES etsy_listings(id),
    product_variant_id INTEGER REFERENCES product_variants(id),
    etsy_property_id VARCHAR(255), -- Etsy's property ID (size, color)
    etsy_value_id VARCHAR(255), -- Etsy's value ID
    sku VARCHAR(255),
    price DECIMAL(10,2),
    quantity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Shopify products (similar structure)
CREATE TABLE shopify_products (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    shopify_shop_id INTEGER REFERENCES shopify_shops(id),
    shopify_product_id VARCHAR(255) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    handle VARCHAR(255), -- URL slug
    status VARCHAR(50), -- 'active', 'draft', 'archived'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Shopify variants
CREATE TABLE shopify_variants (
    id SERIAL PRIMARY KEY,
    shopify_product_id INTEGER REFERENCES shopify_products(id),
    product_variant_id INTEGER REFERENCES product_variants(id),
    shopify_variant_id VARCHAR(255),
    sku VARCHAR(255),
    price DECIMAL(10,2),
    inventory_quantity INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.3 Pricing & Profitability

```sql
-- Fee structures (platform-specific)
CREATE TABLE platform_fee_structures (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL, -- 'etsy', 'shopify'
    fee_type VARCHAR(50) NOT NULL, -- 'listing', 'transaction', 'payment_processing', 'ads'
    fee_percentage DECIMAL(5,2), -- Percentage fee
    fee_fixed DECIMAL(10,2), -- Fixed fee (e.g., $0.20 listing fee)
    min_fee DECIMAL(10,2),
    max_fee DECIMAL(10,2),
    conditions JSONB, -- Additional conditions (e.g., revenue tiers)
    effective_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product pricing rules
CREATE TABLE product_pricing_rules (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_variant_id INTEGER REFERENCES product_variants(id),
    base_cost DECIMAL(10,2), -- Cost from PoD supplier
    markup_percentage DECIMAL(5,2), -- Markup percentage
    markup_fixed DECIMAL(10,2), -- Fixed markup amount
    min_price DECIMAL(10,2), -- Minimum profitable price
    target_margin DECIMAL(5,2), -- Target profit margin
    platform_fees DECIMAL(10,2), -- Calculated platform fees
    final_price DECIMAL(10,2), -- Final selling price
    currency VARCHAR(10) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Discount programs
CREATE TABLE discount_programs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    discount_type VARCHAR(50), -- 'percentage', 'fixed_amount', 'bogo'
    discount_value DECIMAL(10,2),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurrence_pattern VARCHAR(50), -- 'daily', 'weekly', 'monthly', 'yearly'
    min_margin_required DECIMAL(5,2), -- Minimum margin to maintain
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Product-discount mappings
CREATE TABLE product_discount_mappings (
    id SERIAL PRIMARY KEY,
    discount_program_id INTEGER REFERENCES discount_programs(id),
    product_variant_id INTEGER REFERENCES product_variants(id),
    etsy_listing_id INTEGER REFERENCES etsy_listings(id),
    shopify_product_id INTEGER REFERENCES shopify_products(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(discount_program_id, product_variant_id) -- One active discount per product
);
```

#### 4.4 Orders & Fulfillment

```sql
-- Orders from Etsy/Shopify
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    order_number VARCHAR(255) UNIQUE NOT NULL,
    platform VARCHAR(50) NOT NULL, -- 'etsy', 'shopify'
    platform_order_id VARCHAR(255),
    etsy_shop_id INTEGER REFERENCES etsy_shops(id),
    shopify_shop_id INTEGER REFERENCES shopify_shops(id),
    customer_name VARCHAR(255),
    customer_email VARCHAR(255),
    shipping_address JSONB,
    total_amount DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50), -- 'pending', 'processing', 'fulfilled', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Order items
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_variant_id INTEGER REFERENCES product_variants(id),
    design_id INTEGER REFERENCES designs(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2),
    customization_data JSONB, -- Customer customization (text, images, etc.)
    sku VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Fulfillment records
CREATE TABLE fulfillments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    order_item_id INTEGER REFERENCES order_items(id),
    supplier_type VARCHAR(50), -- 'gelato', 'printify', 'printful'
    supplier_connection_id INTEGER REFERENCES supplier_connections(id),
    supplier_order_id VARCHAR(255), -- Order ID from supplier
    status VARCHAR(50), -- 'pending', 'processing', 'shipped', 'delivered', 'failed'
    tracking_number VARCHAR(255),
    shipping_cost DECIMAL(10,2),
    fulfillment_cost DECIMAL(10,2), -- Total cost including printing
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.5 Customization & Mockups

```sql
-- Customer customizations
CREATE TABLE customizations (
    id SERIAL PRIMARY KEY,
    order_item_id INTEGER REFERENCES order_items(id),
    customization_type VARCHAR(50), -- 'text', 'image', 'clipart', 'map'
    field_name VARCHAR(100), -- 'front_text', 'back_image', etc.
    value TEXT, -- Text content or image URL
    position JSONB, -- X, Y coordinates, size, rotation
    font_family VARCHAR(100),
    font_size INTEGER,
    color VARCHAR(7), -- Hex color
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated mockups
CREATE TABLE mockups (
    id SERIAL PRIMARY KEY,
    order_item_id INTEGER REFERENCES order_items(id),
    customization_id INTEGER REFERENCES customizations(id),
    mockup_type VARCHAR(50), -- 'preview', 'production'
    image_url TEXT,
    thumbnail_url TEXT,
    template_id VARCHAR(255), -- Mockup template used
    generated_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.6 Analytics

```sql
-- Sales analytics (aggregated daily)
CREATE TABLE sales_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    platform VARCHAR(50), -- 'etsy', 'shopify', 'all'
    total_revenue DECIMAL(10,2),
    total_orders INTEGER,
    total_items_sold INTEGER,
    total_costs DECIMAL(10,2), -- PoD costs
    total_fees DECIMAL(10,2), -- Platform fees
    net_profit DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, date, platform)
);

-- Product performance
CREATE TABLE product_performance (
    id SERIAL PRIMARY KEY,
    product_variant_id INTEGER REFERENCES product_variants(id),
    period_start DATE,
    period_end DATE,
    views INTEGER DEFAULT 0,
    orders INTEGER DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    profit DECIMAL(10,2) DEFAULT 0,
    conversion_rate DECIMAL(5,2), -- Orders / Views
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 4.7 Subscriptions & Usage (see [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md))

```sql
-- Subscription plan definitions
CREATE TABLE subscription_plans (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL, -- 'free_trial', 'starter', 'growth', 'scale'
    name VARCHAR(100) NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2),
    limits JSONB NOT NULL, -- stores, products, listings, orders/month, storage_mb, mockups/month, etc.
    features JSONB, -- feature flags
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User subscription (current plan, period, trial)
CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id),
    plan_id INTEGER REFERENCES subscription_plans(id),
    status VARCHAR(50) NOT NULL, -- 'trialing', 'active', 'past_due', 'canceled'
    trial_ends_at TIMESTAMP,
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    canceled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking (for limits and overages)
CREATE TABLE usage_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    stores_connected INTEGER DEFAULT 0,
    products_count INTEGER DEFAULT 0,
    listings_count INTEGER DEFAULT 0,
    orders_processed INTEGER DEFAULT 0,
    mockups_generated INTEGER DEFAULT 0,
    storage_bytes BIGINT DEFAULT 0,
    seo_suggestions_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, period_start)
);
```

---

## Part 5: API Integration Plan

### 5.1 Etsy API Integration

**Endpoints Needed:**
- `GET /shops/{shop_id}/listings` - Fetch listings
- `POST /shops/{shop_id}/listings` - Create listing
- `PUT /shops/{shop_id}/listings/{listing_id}` - Update listing
- `GET /shops/{shop_id}/receipts` - Fetch orders
- `POST /shops/{shop_id}/receipts/{receipt_id}/tracking` - Update tracking
- `POST /shops/{shop_id}/coupons` - Create discount codes

**Key Features:**
- OAuth 2.0 authentication
- Rate limiting: 10 requests/second
- Webhook support for order notifications

### 5.2 Shopify API Integration

**Endpoints Needed:**
- `GET /admin/api/2024-01/products.json` - Fetch products
- `POST /admin/api/2024-01/products.json` - Create product
- `PUT /admin/api/2024-01/products/{id}.json` - Update product
- `GET /admin/api/2024-01/orders.json` - Fetch orders
- `POST /admin/api/2024-01/orders/{id}/fulfillments.json` - Create fulfillment
- `POST /admin/api/2024-01/discount_codes.json` - Create discount

**Key Features:**
- OAuth 2.0 authentication
- GraphQL API available (more efficient for bulk operations)
- Webhook support for real-time updates
- Rate limiting: 2 requests/second (40 requests/20 seconds)

### 5.3 PoD Supplier APIs

**Gelato:**
- Product catalog fetching
- Order creation
- Order status tracking

**Printify:**
- Blueprint catalog
- Order creation
- Mockup generation (if available)

**Printful:**
- Product catalog
- Order creation
- Mockup generation API

### 5.4 Mockup Generation (Own Implementation)

**Approach**: Build our own mockup/preview engine. **No third-party mockup APIs at launch.** Use image processing (Pillow, canvas compositing, optional OpenCV) and template-based rendering.

**API design (align with competitors for future integration):**
- **Templates**: Product × placement (e.g. front, back, sleeve). Store template metadata (dimensions, bleed, safe zones).
- **Layers**: Text, image, clipart. Each layer has position, size, rotation, font/color where applicable.
- **Endpoints**: `POST /mockups/preview` (quick preview), `POST /mockups/production` (print-ready). Request: `template_id`, `layers[]`, `options`. Response: `image_url`, `thumbnail_url`, `format`.
- **Rate limiting / usage**: Count previews per user per month; enforce subscription limits (see [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md)). Overage may incur per-preview fee.

**Reference structures**: Customily (layers, placements), Dynamic Mockups (templates, credits). Keep our schema compatible so we can optionally plug in Placeit, Smartmockups, or Printful mockup APIs later.

---

## Part 6: Development Roadmap

### Phase 1: MVP (Months 1-3)

**Sprint 1-2: Foundation**
- Database schema implementation
- User authentication & authorization
- Supplier connection management (existing)
- Basic product catalog from suppliers

**Sprint 3-4: Product & SKU Management**
- Product variant management
- SKU generation system
- Product-supplier mapping
- Inventory tracking

**Sprint 5-6: Listing Management**
- Etsy listing creation (single)
- Shopify product creation (single)
- SKU mapping to listings
- Basic inventory sync

**Sprint 7-8: Pricing & Profitability**
- Fee structure database
- Fee calculator
- Profitability analysis
- Price optimization suggestions

**Sprint 9-10: Order Management**
- Order fetching from Etsy/Shopify
- Order routing to PoD suppliers
- Basic fulfillment tracking

**Sprint 11-12: Dashboard & Analytics**
- Multi-store dashboard
- Basic sales analytics
- Inventory overview

### Phase 2: Growth Features (Months 4-6)

**Sprint 13-14: Bulk Operations**
- Bulk listing creation (CSV import)
- Bulk price updates
- Bulk inventory sync

**Sprint 15-16: SEO Optimization**
- Title optimization
- Tag suggestions
- Description templates
- SEO scoring

**Sprint 17-18: Customization & Mockups**
- Customization data capture
- Mockup generation integration
- Customer preview system
- Production file generation

**Sprint 19-20: Discount System**
- Discount program creation
- Scheduling system
- Platform sync (Etsy/Shopify)
- Margin validation

**Sprint 21-22: Advanced Analytics**
- Product performance tracking
- Design performance analysis
- Profitability reports
- Sales forecasting

### Phase 3: Advanced Features (Months 7-9)

**Sprint 23-24: Design Library**
- Design upload & storage
- Design-product mapping
- Version control
- Canva integration

**Sprint 25-26: Tax & Compliance**
- Tax calculation
- VAT handling
- Compliance reporting

**Sprint 27-28: Optimization & Polish**
- Performance optimization
- UI/UX improvements
- Advanced reporting
- Mobile responsiveness

---

## Part 7: Technical Stack Recommendations

### Backend
- **Framework**: Flask (current) or FastAPI (better for async operations)
- **Database**: PostgreSQL (current)
- **Task Queue**: Celery + Redis (for background jobs)
- **Caching**: Redis
- **File Storage**: AWS S3 or Cloudinary (for designs/mockups)

### Frontend
- **Framework**: React + TypeScript (current)
- **State Management**: Zustand or Redux
- **UI Library**: Tailwind CSS (current)
- **Charts**: Recharts or Chart.js

### Infrastructure
- **Hosting**: Railway (current). See **Part 7.5** for alternatives.
- **CDN**: Cloudflare (for images/mockups)
- **Monitoring**: Sentry (error tracking)
- **Analytics**: Mixpanel or PostHog

### Part 7.5: Hosting Comparison (Railway vs Alternatives)

**Current**: Railway. **Alternatives considered**: Render, Fly.io, AWS (e.g. ECS + RDS).

| Criteria | Railway | Render | Fly.io | AWS (ECS + RDS) |
|----------|---------|--------|--------|------------------|
| **DX / Ease of use** | Excellent; simple deploys, DB attach | Good; straightforward UI | Steeper; CLI, config | Complex; many services |
| **Pricing (mid-scale)** | ~\$5 hobby → ~\$47 mid-scale; usage-based | ~\$7–\$25; transparent, predictable | ~\$15–\$156; confusing model | Variable; often \$50–\$200+ |
| **Database** | Native Postgres, one-click | Native Postgres, managed | DIY or managed | RDS, full control |
| **Bandwidth** | Usage-based; can spike | Transparent; fewer surprises | Usage-based | Per GB; can add up |
| **Scaling** | Auto-scale; good for MVP | Good for apps + workers | Global edge; good for low latency | Highly flexible |
| **Cold starts** | Minimal (long-running) | Minimal | Minimal | None (always-on) |
| **Best for** | Full-stack MVP, small team | Reliable web apps, predictable cost | Global, real-time, edge | Enterprise, compliance |

**Why consider alternatives:**
- **Render**: More predictable pricing and bandwidth; strong uptime; good fit if we want to avoid usage spikes.
- **Fly.io**: Better for global latency, WebSockets, real-time features; more control.
- **AWS**: Best for compliance, scale, and eventual enterprise; higher ops burden.

**Recommendation**: Stay on **Railway** for now (team of 1 + AI, MVP phase). Revisit **Render** when we need predictable monthly cost, or **Fly.io** when we add real-time/mockup workloads and care about global latency.

---

## Part 8: Resolved Questions (See Clarifications Above)

Target users, pricing, mockup approach, hosting, team size, and success metrics are defined in **Clarifications Applied** at the top. Subscription details → [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md). Competitor context → [COMPETITOR_ANALYSIS.md](./COMPETITOR_ANALYSIS.md).

---

## Part 9: Success Metrics

### Business Targets (Clarified)
- **Month 1 (public launch)**: 100 users, **\$2,000/month** subscription revenue.
- **Year 1**: 1,000 users, **\$20,000/month** subscription revenue.
- **Revenue**: Y1 **\$100,000** | Y2 **\$500,000** | Y3 **\$1,000,000**.

### User Engagement
- Daily Active Users (DAU)
- Products managed per user (by plan)
- Listings created per user (by plan)
- Orders processed per user (by plan)

### Business Metrics
- Revenue per user (ARPU)
- Churn rate (target &lt; 5% monthly)
- Customer Lifetime Value (CLV)
- Net Promoter Score (NPS)
- Plan mix (Starter / Growth / Scale)

### Technical Metrics
- API response time (p95 &lt; 500 ms)
- Uptime (target 99.9%)
- Error rate
- Order fulfillment accuracy

---

## Next Steps

1. **Review** this plan and [SUBSCRIPTION_PLANS.md](./SUBSCRIPTION_PLANS.md), [COMPETITOR_ANALYSIS.md](./COMPETITOR_ANALYSIS.md), [FEATURE_PRIORITY.md](./FEATURE_PRIORITY.md).
2. **Confirm** priorities and timeline; adjust roadmaps if needed.
3. **Do not start development yet**; implementation begins only after explicit go-ahead.
4. When approved: **Begin Phase 1** (Sprint 1–2) per roadmap.

---

**Document Version**: 1.1  
**Last Updated**: 2025-01-23  
**Author**: AI Product Manager  
**Changelog**: v1.1 – Clarifications (target users, pricing, tech constraints, success metrics), subscription + usage schema, hosting comparison, mockup own-API, competitor doc refs.
