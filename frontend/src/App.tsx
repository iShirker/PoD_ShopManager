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
import Comparison from './pages/Comparison'
import Templates from './pages/Templates'
import TemplateDetail from './pages/TemplateDetail'
import AuthCallback from './pages/AuthCallback'
import SupplierCallback from './pages/SupplierCallback'
import ShopCallback from './pages/ShopCallback'

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
