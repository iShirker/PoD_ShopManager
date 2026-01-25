import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Shops from './pages/Shops'
import ShopDetail from './pages/ShopDetail'
import Suppliers from './pages/Suppliers'
import Products from './pages/Products'
import ProductsCatalog from './pages/ProductsCatalog'
import Listings from './pages/Listings'
import ListingsBulk from './pages/ListingsBulk'
import ListingsSeo from './pages/ListingsSeo'
import Orders from './pages/Orders'
import OrdersFulfillment from './pages/OrdersFulfillment'
import Pricing from './pages/Pricing'
import PricingRules from './pages/PricingRules'
import Discounts from './pages/Discounts'
import Mockups from './pages/Mockups'
import MockupsTemplates from './pages/MockupsTemplates'
import Designs from './pages/Designs'
import DesignsMappings from './pages/DesignsMappings'
import Analytics from './pages/Analytics'
import AnalyticsProducts from './pages/AnalyticsProducts'
import AnalyticsProfitability from './pages/AnalyticsProfitability'
import SettingsBilling from './pages/SettingsBilling'
import Comparison from './pages/Comparison'
import Templates from './pages/Templates'
import TemplateDetail from './pages/TemplateDetail'
import AuthCallback from './pages/AuthCallback'
import SupplierCallback from './pages/SupplierCallback'
import ShopCallback from './pages/ShopCallback'
import Version from './pages/Version'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/version" element={<Version />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/auth/error" element={<AuthCallback />} />
      <Route path="/suppliers/callback" element={<SupplierCallback />} />
      <Route path="/shops/callback" element={<ShopCallback />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="shops" element={<Shops />} />
        <Route path="shops/:shopId" element={<ShopDetail />} />
        <Route path="suppliers" element={<Suppliers />} />
        <Route path="products" element={<Products />} />
        <Route path="products/catalog" element={<ProductsCatalog />} />
        <Route path="listings" element={<Listings />} />
        <Route path="listings/bulk" element={<ListingsBulk />} />
        <Route path="listings/seo" element={<ListingsSeo />} />
        <Route path="orders" element={<Orders />} />
        <Route path="orders/fulfillment" element={<OrdersFulfillment />} />
        <Route path="pricing" element={<Pricing />} />
        <Route path="pricing/rules" element={<PricingRules />} />
        <Route path="discounts" element={<Discounts />} />
        <Route path="mockups" element={<Mockups />} />
        <Route path="mockups/templates" element={<MockupsTemplates />} />
        <Route path="designs" element={<Designs />} />
        <Route path="designs/mappings" element={<DesignsMappings />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="analytics/products" element={<AnalyticsProducts />} />
        <Route path="analytics/profitability" element={<AnalyticsProfitability />} />
        <Route path="settings/billing" element={<SettingsBilling />} />
        <Route path="comparison" element={<Comparison />} />
        <Route path="templates" element={<Templates />} />
        <Route path="templates/:templateId" element={<TemplateDetail />} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
