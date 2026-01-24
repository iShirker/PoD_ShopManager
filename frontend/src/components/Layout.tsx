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
    title: 'PRODUCTS',
    items: [
      { name: 'My Products', href: '/products', icon: Package },
      { name: 'Catalog', href: '/products/catalog', icon: PackagePlus },
    ],
  },
  {
    title: 'LISTINGS',
    items: [
      { name: 'Listings', href: '/listings', icon: List },
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
    title: 'DISCOUNTS',
    items: [{ name: 'Discount Programs', href: '/discounts', icon: Percent, badge: 'P1' }],
  },
  {
    title: 'CUSTOMIZATION & MOCKUPS',
    items: [
      { name: 'Mockup Studio', href: '/mockups', icon: Image, badge: 'P1' },
      { name: 'Customization Templates', href: '/mockups/templates', icon: LayoutTemplate, badge: 'P1' },
    ],
  },
  {
    title: 'DESIGN LIBRARY',
    items: [
      { name: 'Designs', href: '/designs', icon: Palette, badge: 'P2' },
      { name: 'Product–Design Mappings', href: '/designs/mappings', icon: GitBranch, badge: 'P2' },
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
  {
    title: 'CONNECTIONS',
    items: [
      { name: 'Shops', href: '/shops', icon: Store },
      { name: 'Suppliers', href: '/suppliers', icon: Truck },
    ],
  },
  {
    title: 'TOOLS',
    items: [
      { name: 'Compare Products', href: '/comparison', icon: GitCompare },
      { name: 'Templates', href: '/templates', icon: FileText },
    ],
  },
]

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
              className="flex items-center w-full px-3 py-1.5 text-xs font-semibold text-gray-500 uppercase tracking-wider"
            >
              {!mobile && (isOpen ? <ChevronDown className="w-4 h-4 mr-1" /> : <ChevronRight className="w-4 h-4 mr-1" />)}
              {section.title}
            </button>
            {(mobile || isOpen) &&
              section.items.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={() => mobile && setSidebarOpen(false)}
                  className={({ isActive: active }) =>
                    cn(
                      'flex items-center px-3 py-2 text-sm font-medium rounded-lg mt-0.5',
                      active
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
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
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div className={cn('fixed inset-0 z-50 lg:hidden', sidebarOpen ? 'block' : 'hidden')}>
        <div className="fixed inset-0 bg-gray-900/50" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-xl flex flex-col">
          <div className="flex items-center justify-between px-4 py-4 border-b shrink-0">
            <span className="text-xl font-bold text-primary-600">POD Manager</span>
            <button onClick={() => setSidebarOpen(false)}>
              <X className="w-6 h-6" />
            </button>
          </div>
          {renderNav(true)}
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 bg-white border-r border-gray-200 min-w-0">
          <div className="flex items-center h-16 px-6 border-b border-gray-200 shrink-0">
            <span className="text-xl font-bold text-primary-600">POD Manager</span>
          </div>
          {renderNav(false)}
          <div className="p-4 border-t border-gray-200 shrink-0">
            <div className="flex items-center">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center shrink-0">
                {user?.avatar_url ? (
                  <img src={user.avatar_url} alt="" className="w-10 h-10 rounded-full" />
                ) : (
                  <User className="w-5 h-5 text-primary-600" />
                )}
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-700 truncate">
                  {user?.first_name || user?.username || user?.email}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
            <div className="mt-4 flex flex-col gap-2">
              <NavLink
                to="/profile"
                className="flex items-center justify-center gap-2 btn-secondary text-xs py-2"
              >
                <User className="w-4 h-4" />
                Profile
              </NavLink>
              <NavLink
                to="/settings/billing"
                className="flex items-center justify-center gap-2 btn-secondary text-xs py-2"
              >
                <CreditCard className="w-4 h-4" />
                Billing
              </NavLink>
              <button
                onClick={handleLogout}
                className="flex items-center justify-center gap-2 btn-secondary text-xs py-2 text-red-600 hover:text-red-700"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="lg:pl-64">
        <div className="sticky top-0 z-40 flex items-center h-16 px-4 bg-white border-b border-gray-200 lg:hidden">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu className="w-6 h-6" />
          </button>
          <span className="ml-4 text-lg font-semibold text-primary-600">POD Manager</span>
        </div>
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
