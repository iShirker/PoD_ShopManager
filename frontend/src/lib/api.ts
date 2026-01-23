import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = useAuthStore.getState().refreshToken
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          })

          const { access_token } = response.data
          useAuthStore.getState().setTokens(access_token, refreshToken)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (data: { email: string; password: string; username?: string; first_name?: string; last_name?: string }) =>
    api.post('/auth/register', data),

  logout: () => api.post('/auth/logout'),

  // OAuth for login
  getGoogleAuthUrl: () => api.get('/auth/google/authorize'),

  // OAuth for shop connections
  getEtsyAuthUrl: () => api.get('/auth/etsy/authorize'),
  getShopifyAuthUrl: (shop: string) => api.get(`/auth/shopify/authorize?shop=${shop}`),

  // OAuth for POD suppliers
  getPrintifyAuthUrl: () => api.get('/auth/printify/authorize'),
  getPrintfulAuthUrl: () => api.get('/auth/printful/authorize'),
  getGelatoAuthInfo: () => api.get('/auth/gelato/authorize'),
}

// Users API
export const usersApi = {
  getProfile: () => api.get('/users/me'),
  updateProfile: (data: Partial<{ username: string; first_name: string; last_name: string; avatar_url: string }>) =>
    api.patch('/users/me', data),
  changePassword: (currentPassword: string, newPassword: string) =>
    api.put('/users/me/password', { current_password: currentPassword, new_password: newPassword }),
  getSummary: () => api.get('/users/me/summary'),
}

// Suppliers API
export const suppliersApi = {
  // List all connections
  list: () => api.get('/suppliers'),

  // Get connections for a supplier type
  getByType: (supplierType: string) => api.get(`/suppliers/${supplierType}`),

  // Get specific connection
  getConnection: (connectionId: number) => api.get(`/suppliers/connection/${connectionId}`),

  // Connect new account
  connect: (supplierType: string, apiKey: string, shopId?: string) =>
    api.post(`/suppliers/${supplierType}/connect`, {
      api_key: apiKey,
      shop_id: shopId,
    }),

  // Disconnect (delete) connection by ID
  disconnectConnection: (connectionId: number) =>
    api.post(`/suppliers/connection/${connectionId}/disconnect`),

  // Activate connection
  activateConnection: (connectionId: number) =>
    api.post(`/suppliers/connection/${connectionId}/activate`),

  // Deactivate connection
  deactivateConnection: (connectionId: number) =>
    api.post(`/suppliers/connection/${connectionId}/deactivate`),

  // Sync connection
  syncConnection: (connectionId: number) =>
    api.post(`/suppliers/connection/${connectionId}/sync`),

  // Get products for connection
  getConnectionProducts: (connectionId: number, params?: { page?: number; per_page?: number; search?: string }) =>
    api.get(`/suppliers/connection/${connectionId}/products`, { params }),

  // Legacy: Disconnect all connections of a type
  disconnect: (supplierType: string) => api.post(`/suppliers/${supplierType}/disconnect`),

  // Legacy: Sync all connections of a type
  sync: (supplierType: string) => api.post(`/suppliers/${supplierType}/sync`),

  // Legacy: Get products from all connections of a type
  getProducts: (supplierType: string, params?: { page?: number; per_page?: number; search?: string }) =>
    api.get(`/suppliers/${supplierType}/products`, { params }),

  // Get status summary
  getStatus: () => api.get('/suppliers/status'),
}

// Shops API
export const shopsApi = {
  list: () => api.get('/shops'),
  get: (shopId: number) => api.get(`/shops/${shopId}`),
  connectEtsy: (accessToken: string, refreshToken: string, shopId?: string) =>
    api.post('/shops/etsy/connect', { access_token: accessToken, refresh_token: refreshToken, shop_id: shopId }),
  connectShopify: (accessToken: string, shopDomain: string) =>
    api.post('/shops/shopify/connect', { access_token: accessToken, shop_domain: shopDomain }),
  disconnect: (shopId: number) => api.post(`/shops/${shopId}/disconnect`),
  delete: (shopId: number) => api.delete(`/shops/${shopId}/delete`),
  sync: (shopId: number) => api.post(`/shops/${shopId}/sync`),
  getProducts: (shopId: number, params?: { page?: number; per_page?: number; supplier?: string; search?: string }) =>
    api.get(`/shops/${shopId}/products`, { params }),
}

// Products API
export const productsApi = {
  compare: (params?: { product_type?: string; shop_id?: number; supplier?: string }) =>
    api.get('/products/compare', { params }),
  getComparison: (productId: number) => api.get(`/products/compare/${productId}`),
  getComparisonSummary: () => api.get('/products/compare/summary'),
  switchSupplier: (productId: number, targetSupplier: string, targetProductId?: string) =>
    api.post('/products/switch', { product_id: productId, target_supplier: targetSupplier, target_product_id: targetProductId }),
  bulkSwitch: (productIds: number[], targetSupplier: string) =>
    api.post('/products/switch/bulk', { product_ids: productIds, target_supplier: targetSupplier }),
  getTypes: () => api.get('/products/types'),
  findMatches: (productId: number) => api.get(`/products/match/${productId}`),
}

// Templates API
export const templatesApi = {
  list: (includeProducts?: boolean) =>
    api.get('/templates', { params: { include_products: includeProducts } }),
  get: (templateId: number) => api.get(`/templates/${templateId}`),
  create: (data: {
    name: string;
    description?: string;
    default_title?: string;
    default_description?: string;
    default_tags?: string[];
    default_price_markup?: number;
    target_platforms?: string[];
  }) => api.post('/templates', data),
  update: (templateId: number, data: Partial<{
    name: string;
    description: string;
    default_title: string;
    default_description: string;
    default_tags: string[];
    default_price_markup: number;
    is_active: boolean;
  }>) => api.patch(`/templates/${templateId}`, data),
  delete: (templateId: number) => api.delete(`/templates/${templateId}`),
  addProduct: (templateId: number, data: {
    supplier_type: string;
    product_name: string;
    product_type?: string;
    external_product_id?: string;
    selected_sizes?: string[];
  }) => api.post(`/templates/${templateId}/products`, data),
  updateProduct: (templateId: number, productId: number, data: Partial<{
    product_name: string;
    selected_sizes: string[];
    price_override: number;
  }>) => api.patch(`/templates/${templateId}/products/${productId}`, data),
  deleteProduct: (templateId: number, productId: number) =>
    api.delete(`/templates/${templateId}/products/${productId}`),
  addColor: (templateId: number, productId: number, data: {
    color_name: string;
    color_hex?: string;
    display_name?: string;
  }) => api.post(`/templates/${templateId}/products/${productId}/colors`, data),
  deleteColor: (templateId: number, productId: number, colorId: number) =>
    api.delete(`/templates/${templateId}/products/${productId}/colors/${colorId}`),
  createListing: (templateId: number, data: {
    shop_id: number;
    title?: string;
    description?: string;
    price?: number;
    tags?: string[];
    images?: string[];
  }) => api.post(`/templates/${templateId}/create-listing`, data),
  preview: (templateId: number, data?: {
    title?: string;
    description?: string;
    tags?: string[];
  }) => api.post(`/templates/${templateId}/preview`, data),
}

export default api
