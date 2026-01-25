export type HelpInstructionBlock = {
  title: string
  steps: string[]
}

export type HelpEntry = {
  /** Canonical route prefix (e.g. `/products/catalog`). */
  route: string
  /** Human title shown in the Help modal. */
  title: string
  /** What this screen is designed for. */
  designedFor: string
  /** End-user value: primary features the screen provides. */
  features: string[]
  /** Business/domain objects the screen operates on. */
  objects: string[]
  /** Step-by-step instructions for the common actions on the screen. */
  instructions: HelpInstructionBlock[]
  /** Optional doc filename in repo `docs/pages/*.md` (shown as “More details”). */
  docFile?: string
}

// Keep these entries aligned with main navigation routes and docs/pages/*.md names.
export const helpRegistry: HelpEntry[] = [
  {
    route: '/',
    title: 'Dashboard',
    designedFor:
      'A fast “at-a-glance” overview of your business health: connected shops/suppliers, recent activity, and where to go next.',
    features: [
      'Quick status of connected Shops (Etsy/Shopify) and Suppliers (Printify/Printful/Gelato)',
      'High-level KPIs (sales, orders, costs/profit) when data is available',
      'Shortcuts to the most common workflows (Products, Catalog, Orders, Comparison)',
    ],
    objects: ['Shop', 'SupplierConnection', 'Product / UserProduct', 'Order', 'PricingRule (read-only summary)'],
    instructions: [
      {
        title: 'Use the overview',
        steps: [
          'Scan connection cards first: fix any “disconnected” or “error” states before troubleshooting data issues.',
          'Use KPI tiles to spot anomalies (e.g., sudden order drop, unusual cost increase).',
          'Use the shortcuts to jump into Products, Catalog, or Orders depending on what you want to do next.',
        ],
      },
    ],
    docFile: 'Dashboard.md',
  },
  {
    route: '/shops',
    title: 'Shops',
    designedFor: 'Connect and manage your selling channels (Etsy and Shopify) and keep listings/orders synced.',
    features: [
      'Connect new shops via OAuth',
      'See connection status and last sync time',
      'Sync products/listings and orders into the app database',
      'Open shop detail to inspect and troubleshoot a specific connection',
    ],
    objects: ['Shop (Etsy/Shopify connection)', 'Listing / Product', 'Order', 'Fulfillment', 'Webhook events (future)'],
    instructions: [
      {
        title: 'Connect a shop',
        steps: [
          'Click “Connect Etsy” or “Connect Shopify”.',
          'Complete authorization in the popup/redirect and return to the app.',
          'Verify the shop appears as “Connected”. If you see an error, open Shop Detail and review the message.',
        ],
      },
      {
        title: 'Sync data',
        steps: [
          'Use “Sync” to pull latest products/listings and orders.',
          'If data looks incomplete, re-check platform permissions/scopes and retry sync.',
        ],
      },
    ],
    docFile: 'Shops.md',
  },
  {
    route: '/shops/:shopId',
    title: 'Shop Detail',
    designedFor: 'Inspect one shop connection in depth: metadata, sync history, errors, and linked products/orders.',
    features: ['View connection details', 'Troubleshoot auth/sync issues', 'Run targeted sync actions'],
    objects: ['Shop', 'Listing / Product', 'Order', 'OAuth tokens (metadata only)'],
    instructions: [
      {
        title: 'Troubleshoot a connection',
        steps: [
          'Review the latest error text and time (if present).',
          'Retry sync after fixing the cause (expired token, missing permissions, etc.).',
          'If issues persist, disconnect and reconnect to regenerate tokens.',
        ],
      },
    ],
    docFile: 'ShopDetail.md',
  },
  {
    route: '/suppliers',
    title: 'Suppliers',
    designedFor: 'Connect and manage PoD suppliers (Printify, Printful, Gelato) and keep supplier catalogs synced.',
    features: [
      'Connect supplier accounts (API key or OAuth, depending on supplier)',
      'See connection status and active account',
      'Sync supplier catalogs into the app for browsing and matching',
    ],
    objects: ['SupplierConnection', 'SupplierProduct (catalog entries)', 'UserProduct (when added from catalog)'],
    instructions: [
      {
        title: 'Connect a supplier',
        steps: [
          'Choose supplier (Printify / Printful / Gelato).',
          'Provide the required credential (API key/token) or use OAuth connect if available.',
          'If multiple accounts exist, keep only the intended account “Active” for comparisons.',
        ],
      },
      {
        title: 'Sync supplier catalog',
        steps: [
          'Click “Sync” to import supplier catalog products into the app database.',
          'After sync, use Catalog page to browse and add products to “My Products”.',
        ],
      },
    ],
    docFile: 'Suppliers.md',
  },
  {
    route: '/products',
    title: 'My Products',
    designedFor: 'Maintain your internal product list: items you plan to list/sell and compare across suppliers.',
    features: ['Search and filter your products', 'Inspect supplier + SKU info', 'Jump into comparison/switching flows'],
    objects: ['UserProduct', 'UserProductSupplier', 'SupplierProduct', 'SKU mapping'],
    instructions: [
      {
        title: 'Add a product to your list',
        steps: ['Go to Catalog, choose a supplier product, and click “Add”.', 'Return here to see it in your list.'],
      },
      {
        title: 'Find products quickly',
        steps: [
          'Use Search to filter by product name, brand/model, or product type.',
          'Use supplier filters to focus on one supplier’s offerings.',
        ],
      },
      {
        title: 'Compare and optimize cost',
        steps: [
          'Use “Compare” to see base cost + shipping estimate across connected suppliers.',
          'If savings are meaningful, switch primary supplier (where supported) to reduce cost.',
        ],
      },
    ],
    docFile: 'Products.md',
  },
  {
    route: '/products/catalog',
    title: 'Catalog',
    designedFor:
      'Browse supplier catalogs (Printify/Printful/Gelato) and add products into your internal “My Products” list.',
    features: [
      'Browse products by supplier connection',
      'Search and filter by category',
      'Add a supplier product to “My Products” and auto-detect matches on other suppliers',
    ],
    objects: ['SupplierConnection', 'SupplierProduct (catalog result)', 'UserProduct', 'UserProductSupplier'],
    instructions: [
      {
        title: 'Browse a supplier catalog',
        steps: [
          'Select a supplier account/connection.',
          'Use Category filter to narrow down the catalog.',
          'Use Search to find a specific brand/model (e.g., “Gildan 18000”, “Bella Canvas 3001”).',
        ],
      },
      {
        title: 'Add a product',
        steps: [
          'Open a product row/card.',
          'Click “Add to My Products”.',
          'Review matched suppliers (if found) to set up comparisons immediately.',
        ],
      },
    ],
    docFile: 'ProductsCatalog.md',
  },
  {
    route: '/comparison',
    title: 'Compare & Switch',
    designedFor: 'Compare production cost across suppliers and switch products to lower-cost suppliers safely.',
    features: [
      'Compare base cost + shipping estimate across suppliers',
      'Highlight best supplier and potential savings',
      'Switch supplier for a product (and update SKUs as needed)',
    ],
    objects: ['Product (store-linked)', 'UserProduct', 'SupplierConnection', 'SupplierProduct', 'SKU mapping'],
    instructions: [
      {
        title: 'Run a comparison',
        steps: [
          'Ensure at least one supplier account is connected (Suppliers page).',
          'Use filters (product type, shop, current supplier) to narrow results.',
          'Review “best supplier” and “potential savings” for each product type.',
        ],
      },
      {
        title: 'Switch supplier (carefully)',
        steps: [
          'Pick the target supplier with the best total cost (base + shipping).',
          'Run “Switch” and review SKU changes.',
          'After switching, confirm marketplace listing variants have updated SKUs (if applicable).',
        ],
      },
    ],
    docFile: 'Comparison.md',
  },
  {
    route: '/listings',
    title: 'Listings',
    designedFor: 'Manage your live marketplace listings (Etsy/Shopify) and map them to your templates/products.',
    features: ['Browse listings across connected shops', 'Inspect listing status', 'Prepare for bulk actions'],
    objects: ['Listing (Etsy/Shopify)', 'Variant', 'Template', 'Product / SKU mapping'],
    instructions: [
      {
        title: 'Review listings',
        steps: [
          'Use shop filters to focus on one marketplace.',
          'Open a listing to inspect variants (size/color), SKUs, and status.',
          'Use mapping fields (where provided) to link listing variants to your internal product/template.',
        ],
      },
    ],
    docFile: 'Listings.md',
  },
  {
    route: '/listings/bulk',
    title: 'Bulk Create',
    designedFor: 'Create or update multiple listings in one workflow (template-driven publishing).',
    features: ['Batch creation plan', 'Validation before publish', 'Track job progress and errors'],
    objects: ['Template', 'DesignAsset', 'Listing draft', 'Shop channel (Etsy/Shopify)'],
    instructions: [
      {
        title: 'Bulk-create workflow',
        steps: [
          'Select target shop/channel.',
          'Choose a template and one or more designs.',
          'Configure prices/tags/SEO rules.',
          'Run validation, then publish the batch and review results.',
        ],
      },
    ],
    docFile: 'ListingsBulk.md',
  },
  {
    route: '/listings/seo',
    title: 'SEO Assistant',
    designedFor: 'Improve listing discoverability with suggestions and bulk edits (titles, tags, descriptions).',
    features: ['Keyword suggestions', 'Bulk tag/title operations', 'Preview before applying to listings'],
    objects: ['Listing', 'SEO suggestion', 'Keyword set', 'Platform constraints (Etsy/Shopify)'],
    instructions: [
      {
        title: 'Apply SEO improvements',
        steps: [
          'Choose listing(s) or a filter set (shop, status, product type).',
          'Review suggested keywords/tags and title changes.',
          'Apply changes and confirm updates were pushed to the marketplace.',
        ],
      },
    ],
    docFile: 'ListingsSeo.md',
  },
  {
    route: '/templates',
    title: 'Templates',
    designedFor: 'Create reusable product templates that standardize variants, print placements, pricing rules, and SEO.',
    features: ['Template list and search', 'Create/edit templates', 'Use templates in bulk create flows'],
    objects: ['Template', 'Placement/print area', 'Variant options', 'Default pricing/SEO rules'],
    instructions: [
      {
        title: 'Create a template',
        steps: [
          'Click “New Template”.',
          'Define product type/variants (sizes/colors) and print placements.',
          'Save, then use the template in Bulk Create or Mockup workflows.',
        ],
      },
    ],
    docFile: 'Templates.md',
  },
  {
    route: '/templates/:templateId',
    title: 'Template Detail',
    designedFor: 'Edit one template in depth and validate it can produce consistent listings across channels/suppliers.',
    features: ['Edit fields and placements', 'Validate variant set', 'Preview how it will be used for listing creation'],
    objects: ['Template', 'Variant options', 'Artwork placements', 'Pricing/SEO defaults'],
    instructions: [
      {
        title: 'Maintain a template',
        steps: [
          'Update variants only when you can support them in your supplier catalog.',
          'Keep placement names consistent (e.g., “front”, “back”).',
          'Save changes and re-test bulk creation on a small batch first.',
        ],
      },
    ],
    docFile: 'TemplateDetail.md',
  },
  {
    route: '/orders',
    title: 'Orders',
    designedFor: 'Track incoming marketplace orders and prepare them for fulfillment.',
    features: ['View orders by shop/status', 'Inspect line items and addresses', 'Navigate to fulfillment workflow'],
    objects: ['Order', 'OrderLineItem', 'Customer', 'Address', 'Shop'],
    instructions: [
      {
        title: 'Process orders',
        steps: [
          'Filter by shop and fulfillment status to find what needs attention.',
          'Open an order to confirm shipping address and SKU mapping.',
          'Send to Fulfillment when ready (or fix mapping issues first).',
        ],
      },
    ],
    docFile: 'Orders.md',
  },
  {
    route: '/orders/fulfillment',
    title: 'Fulfillment',
    designedFor: 'Create supplier fulfillment orders and track shipments back to the customer.',
    features: ['Fulfillment queue', 'Create supplier orders', 'Tracking updates and shipment status'],
    objects: ['SupplierOrder', 'Shipment', 'Order', 'SupplierConnection', 'SKU mapping'],
    instructions: [
      {
        title: 'Fulfill an order',
        steps: [
          'Pick an order from the queue.',
          'Confirm each line item is mapped to the correct supplier product/variant.',
          'Submit to supplier and record the supplier order ID.',
          'Monitor tracking updates (preferably via webhooks).',
        ],
      },
    ],
    docFile: 'OrdersFulfillment.md',
  },
  {
    route: '/pricing',
    title: 'Calculator',
    designedFor: 'Calculate prices and margins using platform fees, shipping, and supplier costs.',
    features: ['Price/margin calculator', 'Scenario testing', 'Export or apply as rule baseline'],
    objects: ['Money', 'Fee settings', 'Supplier base cost', 'Shipping estimate', 'Margin target'],
    instructions: [
      {
        title: 'Calculate a target price',
        steps: [
          'Enter product cost and shipping estimate (supplier-side).',
          'Select platform (Etsy/Shopify) fee model if applicable.',
          'Set desired profit or margin %, then compute recommended price.',
        ],
      },
    ],
    docFile: 'Pricing.md',
  },
  {
    route: '/pricing/rules',
    title: 'Price Rules',
    designedFor: 'Define reusable pricing rules to apply consistent pricing across listings and variants.',
    features: ['Create/edit/delete rules', 'Rule precedence', 'Apply rules during bulk create or updates'],
    objects: ['PricingRule', 'Variant', 'Listing', 'ProductTypeKey'],
    instructions: [
      {
        title: 'Create a rule',
        steps: [
          'Define the target (product type, supplier, category).',
          'Choose a pricing formula (markup, fixed profit, rounding).',
          'Save and test on a small sample before mass applying.',
        ],
      },
    ],
    docFile: 'PricingRules.md',
  },
  {
    route: '/discounts',
    title: 'Discounts',
    designedFor: 'Plan and manage promotional discounts across listings and channels.',
    features: ['Define discount campaigns', 'Scope by listing set', 'Measure impact in analytics'],
    objects: ['DiscountCampaign', 'Listing', 'Order metrics'],
    instructions: [
      {
        title: 'Run a discount campaign',
        steps: [
          'Choose the target listings and discount %/amount.',
          'Set start/end dates and channel rules.',
          'After launch, review performance in Analytics.',
        ],
      },
    ],
    docFile: 'Discounts.md',
  },
  {
    route: '/mockups',
    title: 'Mockup Studio',
    designedFor: 'Create marketplace-ready mockups using your designs and product templates.',
    features: ['Choose templates and designs', 'Generate mockups', 'Export for listings'],
    objects: ['DesignAsset', 'Mockup', 'Template', 'Placement'],
    instructions: [
      {
        title: 'Generate mockups',
        steps: [
          'Select a template/product type.',
          'Pick a design and assign it to placements (front/back/etc.).',
          'Generate mockups and download the images for listing uploads.',
        ],
      },
    ],
    docFile: 'Mockups.md',
  },
  {
    route: '/mockups/templates',
    title: 'Customization Templates',
    designedFor: 'Create reusable mockup/placement presets to speed up mockup generation.',
    features: ['Define placement presets', 'Reuse across products', 'Standardize output'],
    objects: ['MockupTemplate', 'Placement', 'Design mapping rules'],
    instructions: [
      {
        title: 'Create a preset',
        steps: [
          'Define placement areas and naming conventions.',
          'Save as a reusable template.',
          'Use it in Mockup Studio to apply placements consistently.',
        ],
      },
    ],
    docFile: 'MockupsTemplates.md',
  },
  {
    route: '/designs',
    title: 'Designs',
    designedFor: 'Manage your reusable design assets (the artwork you apply to products and listings).',
    features: ['Upload and organize designs', 'Search by tags/collections', 'Use in templates/mockups/bulk create'],
    objects: ['DesignAsset', 'Tag/Collection', 'File metadata'],
    instructions: [
      {
        title: 'Manage design assets',
        steps: [
          'Upload designs with clear names and tags.',
          'Organize designs into collections for bulk creation.',
          'Reuse designs in Templates, Mockups, and Listings workflows.',
        ],
      },
    ],
    docFile: 'Designs.md',
  },
  {
    route: '/designs/mappings',
    title: 'Design Mappings',
    designedFor: 'Define how designs map to templates, placements, and product types (to automate repeatable work).',
    features: ['Rules-based mapping', 'Placement assignment', 'Consistency checks'],
    objects: ['DesignAsset', 'Template', 'Placement', 'MappingRule'],
    instructions: [
      {
        title: 'Create a mapping rule',
        steps: [
          'Choose a trigger (product type, template, tag/collection).',
          'Specify placements and default scaling/alignment rules.',
          'Save and test in Mockup Studio or Bulk Create.',
        ],
      },
    ],
    docFile: 'DesignsMappings.md',
  },
  {
    route: '/analytics',
    title: 'Analytics Overview',
    designedFor: 'Monitor business performance and identify what to optimize (pricing, products, suppliers, listings).',
    features: ['KPIs and trends', 'Filter by shop/date range', 'Jump into deeper analytics pages'],
    objects: ['Order metrics', 'Revenue/Cost/Profit', 'ProductTypeKey', 'Shop'],
    instructions: [
      {
        title: 'Use analytics to decide next actions',
        steps: [
          'Start with Overview to spot changes over time.',
          'Use Product Performance to identify winners/losers.',
          'Use Profitability Reports to find margin leaks (fees, shipping, supplier costs).',
        ],
      },
    ],
    docFile: 'Analytics.md',
  },
  {
    route: '/analytics/products',
    title: 'Product Performance',
    designedFor: 'Understand which products perform best so you can scale winners and fix/retire losers.',
    features: ['Per-product metrics', 'Filters by period/shop/type', 'Sorting and comparisons'],
    objects: ['Product', 'Listing', 'Order metrics', 'Traffic metrics (if available)'],
    instructions: [
      {
        title: 'Analyze product performance',
        steps: [
          'Select a time period and (optionally) a shop.',
          'Sort by revenue or margin to identify top performers.',
          'Investigate low-margin products and consider supplier switch or pricing rule updates.',
        ],
      },
    ],
    docFile: 'AnalyticsProducts.md',
  },
  {
    route: '/analytics/profitability',
    title: 'Profitability Reports',
    designedFor: 'Break down profitability (fees, shipping, supplier costs) to increase margin and reduce surprises.',
    features: ['Profit breakdown', 'Filters and grouping', 'Export/reporting'],
    objects: ['Order', 'Money', 'Fees', 'Supplier costs', 'Shipping costs'],
    instructions: [
      {
        title: 'Find margin leaks',
        steps: [
          'Filter by shop and date range.',
          'Group by product type to see which categories are underperforming.',
          'Apply pricing rules or switch suppliers where it improves total cost.',
        ],
      },
    ],
    docFile: 'AnalyticsProfitability.md',
  },
  {
    route: '/profile',
    title: 'Profile',
    designedFor: 'Manage your account settings and personal information.',
    features: ['View/update profile info', 'Security and session controls'],
    objects: ['User'],
    instructions: [
      {
        title: 'Maintain your profile',
        steps: ['Update your display name and account details as needed.', 'Log out on shared devices.'],
      },
    ],
    docFile: 'Profile.md',
  },
  {
    route: '/settings/billing',
    title: 'Billing',
    designedFor: 'Manage subscription, payment method, and billing status.',
    features: ['View plan', 'Upgrade/downgrade', 'Payment status and invoices (when enabled)'],
    objects: ['SubscriptionPlan', 'BillingStatus', 'Invoice (future)'],
    instructions: [
      {
        title: 'Manage billing',
        steps: [
          'Review your current plan and limits.',
          'Update payment method if you see failed payment warnings.',
          'Use upgrade if you need more connected stores/suppliers or higher sync volume.',
        ],
      },
    ],
    docFile: 'SettingsBilling.md',
  },
]

function normalizePathname(pathname: string) {
  // Remove trailing slash (except root).
  if (pathname.length > 1 && pathname.endsWith('/')) return pathname.slice(0, -1)
  return pathname
}

function routeToMatcherPrefix(route: string) {
  // Convert `/shops/:shopId` to `/shops/` for prefix matching.
  if (!route.includes(':')) return route
  return route.replace(/:\w+/g, '')
}

/**
 * Returns the most specific help entry for the current pathname, using longest-prefix match.
 *
 * Examples:
 * - pathname `/products/catalog` → match `/products/catalog`
 * - pathname `/shops/123` → match `/shops/:shopId` (falls back to `/shops` if not present)
 */
export function getHelpEntryForPath(pathnameRaw: string): HelpEntry | null {
  const pathname = normalizePathname(pathnameRaw)

  let best: { entry: HelpEntry; score: number } | null = null

  for (const entry of helpRegistry) {
    const prefix = routeToMatcherPrefix(entry.route)
    if (prefix === '/') {
      if (pathname === '/') {
        const score = 1
        if (!best || score > best.score) best = { entry, score }
      }
      continue
    }

    if (pathname === prefix || pathname.startsWith(prefix)) {
      const score = prefix.length
      if (!best || score > best.score) best = { entry, score }
    }
  }

  return best?.entry ?? null
}

