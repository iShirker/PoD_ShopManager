import { useState } from 'react'
import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import {
  LayoutDashboard,
  Store,
  Package,
  PackagePlus,
  List,
  Layers,
  Search,
  ShoppingCart,
  Truck,
  Calculator,
  Sliders,
  Percent,
  Image,
  LayoutTemplate,
  Palette,
  GitBranch,
  BarChart2,
  TrendingUp,
  DollarSign,
  GitCompare,
  FileText,
  User,
  CreditCard,
  LogOut,
  Menu,
  X,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { cn } from '../lib/utils'

export interface NavItem {
  name: string
  href: string
  icon: React.ElementType
  badge?: 'P1' | 'P2'
}

export interface NavSection {
  title: string
  items: NavItem[]
}

const navSections: NavSection[] = [
  {
    title: 'OVERVIEW',
    items: [{ name: 'Dashboard', href: '/', icon: LayoutDashboard }],
  },
  {
    title: 'CONNECTIONS',
    items: [
      { name: 'Shops', href: '/shops', icon: Store },
      { name: 'Suppliers', href: '/suppliers', icon: Truck },
    ],
  },
  {
    title: 'PRODUCTS',
    items: [
      { name: 'My Products', href: '/products', icon: Package },
      { name: 'Catalog', href: '/products/catalog', icon: PackagePlus },
      { name: 'Compare & Switch', href: '/comparison', icon: GitCompare },
    ],
  },
  {
    title: 'LISTINGS',
    items: [
      { name: 'Listings', href: '/listings', icon: List },
      { name: 'Templates', href: '/templates', icon: FileText },
      { name: 'Bulk Create', href: '/listings/bulk', icon: Layers, badge: 'P1' },
      { name: 'SEO Assistant', href: '/listings/seo', icon: Search, badge: 'P1' },
    ],
  },
  {
    title: 'ORDERS',
    items: [
      { name: 'Orders', href: '/orders', icon: ShoppingCart },
      { name: 'Fulfillment', href: '/orders/fulfillment', icon: Truck },
    ],
  },
  {
    title: 'PRICING & PROFITABILITY',
    items: [
      { name: 'Calculator', href: '/pricing', icon: Calculator },
      { name: 'Price Rules', href: '/pricing/rules', icon: Sliders },
    ],
  },
  {
    title: 'PROMOTIONS',
    items: [{ name: 'Discounts', href: '/discounts', icon: Percent, badge: 'P1' }],
  },
  {
    title: 'MOCKUPS & CUSTOMIZATION',
    items: [
      { name: 'Mockup Studio', href: '/mockups', icon: Image, badge: 'P1' },
      { name: 'Customization Templates', href: '/mockups/templates', icon: LayoutTemplate, badge: 'P1' },
    ],
  },
  {
    title: 'DESIGN LIBRARY',
    items: [
      { name: 'Designs', href: '/designs', icon: Palette, badge: 'P2' },
      { name: 'Design Mappings', href: '/designs/mappings', icon: GitBranch, badge: 'P2' },
    ],
  },
  {
    title: 'ANALYTICS',
    items: [
      { name: 'Overview', href: '/analytics', icon: BarChart2 },
      { name: 'Product Performance', href: '/analytics/products', icon: TrendingUp, badge: 'P2' },
      { name: 'Profitability Reports', href: '/analytics/profitability', icon: DollarSign, badge: 'P2' },
    ],
  },
]

const navItemHrefs = navSections.flatMap((s) => s.items.map((i) => i.href))

/**
 * If a nav item has a child route *also present in the menu*, we want the parent
 * item to match EXACTLY (so it doesn't stay highlighted together with its child).
 *
 * Example:
 * - /products and /products/catalog are both menu items
 * - when on /products/catalog, only Catalog should be active (not My Products)
 */
function shouldNavLinkEnd(href: string) {
  if (href === '/') return true
  return navItemHrefs.some((h) => h !== href && h.startsWith(href + '/'))
}

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (href: string) => {
    if (href === '/') return location.pathname === '/'
    return location.pathname === href || location.pathname.startsWith(href + '/')
  }

  const renderNav = (mobile = false) => (
    <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
      {navSections.map((section) => {
        const hasActive = section.items.some((i) => isActive(i.href))
        const isCollapsed = collapsed[section.title] === true
        const isOpen = collapsed[section.title] !== undefined ? !isCollapsed : hasActive
        return (
          <div key={section.title} className="mb-4">
            <button
              type="button"
              onClick={() => !mobile && setCollapsed((c) => ({ ...c, [section.title]: isOpen }))}
              className="app-nav-section flex items-center w-full px-3 py-1.5 uppercase tracking-wider"
            >
              {!mobile && (isOpen ? <ChevronDown className="w-4 h-4 mr-1" /> : <ChevronRight className="w-4 h-4 mr-1" />)}
              {section.title}
            </button>
            {(mobile || isOpen) &&
              section.items.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  end={shouldNavLinkEnd(item.href)}
                  onClick={() => mobile && setSidebarOpen(false)}
                  className={({ isActive: active }) =>
                    cn(
                      'app-nav-link flex items-center px-3 py-2 text-sm font-medium rounded-lg mt-0.5',
                      active && 'active'
                    )
                  }
                >
                  <item.icon className="w-5 h-5 mr-3 shrink-0" />
                  <span className="flex-1 truncate">{item.name}</span>
                  {item.badge && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-200 text-gray-600">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
          </div>
        )
      })}
    </nav>
  )

  return (
    <div className="min-h-screen app-main">
      {/* Mobile sidebar */}
      <div className={cn('fixed inset-0 z-50 lg:hidden', sidebarOpen ? 'block' : 'hidden')}>
        <div className="fixed inset-0 bg-black/50" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 w-64 app-sidebar shadow-xl flex flex-col min-w-0">
          <div className="flex items-center justify-between px-4 py-4 border-b shrink-0" style={{ borderColor: 'var(--t-sidebar-border)' }}>
            <span className="text-xl font-bold app-logo">POD Manager</span>
            <button onClick={() => setSidebarOpen(false)} className="app-nav-link p-1 rounded">
              <X className="w-6 h-6" />
            </button>
          </div>
          {renderNav(true)}
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 app-sidebar min-w-0">
          <div className="flex items-center h-16 px-6 border-b shrink-0" style={{ borderColor: 'var(--t-sidebar-border)' }}>
            <span className="text-xl font-bold app-logo">POD Manager</span>
          </div>
          {renderNav(false)}
          <div className="p-4 border-t shrink-0" style={{ borderColor: 'var(--t-sidebar-border)' }}>
            <div className="flex items-center">
              <div className="w-10 h-10 rounded-full flex items-center justify-center shrink-0" style={{ background: 'var(--t-sidebar-active-bg)', color: 'var(--t-sidebar-active-text)' }}>
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />
                ) : (
                  <User className="w-5 h-5" />
                )}
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium truncate" style={{ color: 'var(--t-sidebar-active-text)' }}>
                  {user?.first_name || user?.username || user?.email}
                </p>
                <p className="text-xs truncate text-muted">{user?.email}</p>
              </div>
            </div>
            <div className="mt-4 flex flex-col gap-2">
              <NavLink to="/profile" className="flex items-center justify-center gap-2 btn-secondary text-xs py-2">
                <User className="w-4 h-4" />
                Profile
              </NavLink>
              <NavLink to="/settings/billing" className="flex items-center justify-center gap-2 btn-secondary text-xs py-2">
                <CreditCard className="w-4 h-4" />
                Billing
              </NavLink>
              <button onClick={handleLogout} className="flex items-center justify-center gap-2 btn-secondary text-xs py-2 text-red-600 hover:text-red-700">
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="lg:pl-64">
        <div className="sticky top-0 z-40 flex items-center h-16 px-4 card lg:hidden" style={{ borderRadius: 0, borderLeft: 'none', borderTop: 'none', borderRight: 'none' }}>
          <button onClick={() => setSidebarOpen(true)} className="app-nav-link p-1 rounded">
            <Menu className="w-6 h-6" />
          </button>
          <span className="ml-4 text-lg font-semibold app-logo">POD Manager</span>
        </div>
        <main className="app-main p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
