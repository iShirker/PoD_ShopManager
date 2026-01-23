import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { templatesApi, suppliersApi, shopsApi } from '../lib/api'
import { getSupplierColor, getSupplierName } from '../lib/utils'
import { cn } from '../lib/utils'
import ProductPricing from '../components/ProductPricing'
import {
  ArrowLeft, Plus, Trash2, Loader2, X, Package, Edit2, DollarSign
} from 'lucide-react'

export default function TemplateDetail() {
  const { templateId } = useParams<{ templateId: string }>()
  const queryClient = useQueryClient()

  const [showAddProduct, setShowAddProduct] = useState(false)
  const [showAddColor, setShowAddColor] = useState<number | null>(null)
  const [showCreateListing, setShowCreateListing] = useState(false)
  const [editingProduct, setEditingProduct] = useState<number | null>(null)
  const [showPricing, setShowPricing] = useState<number | null>(null)

  const { data: template, isLoading } = useQuery({
    queryKey: ['template', templateId],
    queryFn: () => templatesApi.get(Number(templateId)),
    enabled: !!templateId,
  })

  const { data: suppliers } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => suppliersApi.list(),
  })

  const { data: shops } = useQuery({
    queryKey: ['shops'],
    queryFn: () => shopsApi.list(),
  })

  const { register, handleSubmit } = useForm()

  const updateMutation = useMutation({
    mutationFn: (data: any) => templatesApi.update(Number(templateId), data),
    onSuccess: () => {
      toast.success('Template updated')
      queryClient.invalidateQueries({ queryKey: ['template', templateId] })
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update')
    },
  })

  const addProductMutation = useMutation({
    mutationFn: (data: any) => templatesApi.addProduct(Number(templateId), data),
    onSuccess: () => {
      toast.success('Product added')
      queryClient.invalidateQueries({ queryKey: ['template', templateId] })
      setShowAddProduct(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to add product')
    },
  })

  const deleteProductMutation = useMutation({
    mutationFn: (productId: number) =>
      templatesApi.deleteProduct(Number(templateId), productId),
    onSuccess: () => {
      toast.success('Product removed')
      queryClient.invalidateQueries({ queryKey: ['template', templateId] })
    },
  })

  const addColorMutation = useMutation({
    mutationFn: ({ productId, data }: { productId: number; data: any }) =>
      templatesApi.addColor(Number(templateId), productId, data),
    onSuccess: () => {
      toast.success('Color added')
      queryClient.invalidateQueries({ queryKey: ['template', templateId] })
      setShowAddColor(null)
    },
  })

  const deleteColorMutation = useMutation({
    mutationFn: ({ productId, colorId }: { productId: number; colorId: number }) =>
      templatesApi.deleteColor(Number(templateId), productId, colorId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['template', templateId] })
    },
  })

  const updateProductMutation = useMutation({
    mutationFn: ({ productId, data }: { productId: number; data: any }) =>
      templatesApi.updateProduct(Number(templateId), productId, data),
    onSuccess: () => {
      toast.success('Product updated')
      queryClient.invalidateQueries({ queryKey: ['template', templateId] })
      queryClient.invalidateQueries({ queryKey: ['template-product-pricing'] })
      setEditingProduct(null)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to update product')
    },
  })

  const createListingMutation = useMutation({
    mutationFn: (data: any) => templatesApi.createListing(Number(templateId), data),
    onSuccess: () => {
      toast.success('Listing created')
      setShowCreateListing(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create listing')
    },
  })

  const templateData = template?.data
  const suppliersList = suppliers?.data?.suppliers || []
  const connectedSuppliers = suppliersList.filter((s: any) => s.is_connected)
  const shopsList = shops?.data?.shops || []

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/templates" className="btn-secondary p-2">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{templateData?.name}</h1>
            <p className="text-gray-500">{templateData?.description}</p>
          </div>
        </div>
        <button
          onClick={() => setShowCreateListing(true)}
          disabled={!templateData?.products?.length}
          className="btn-primary"
        >
          <Plus className="w-5 h-5 mr-2" />
          Create Listing
        </button>
      </div>

      {/* Template Settings */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-semibold">Template Settings</h2>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">Default Title</label>
              <input
                type="text"
                defaultValue={templateData?.default_title || ''}
                onChange={(e) =>
                  updateMutation.mutate({ default_title: e.target.value })
                }
                className="input"
                placeholder="Default listing title"
              />
            </div>
            <div>
              <label className="label">Price Markup (%)</label>
              <input
                type="number"
                defaultValue={templateData?.default_price_markup || 0}
                onChange={(e) =>
                  updateMutation.mutate({
                    default_price_markup: Number(e.target.value),
                  })
                }
                className="input"
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="label">Default Description</label>
            <textarea
              defaultValue={templateData?.default_description || ''}
              onChange={(e) =>
                updateMutation.mutate({ default_description: e.target.value })
              }
              className="input"
              rows={3}
              placeholder="Default listing description"
            />
          </div>
        </div>
      </div>

      {/* Products */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Products ({templateData?.products?.length || 0})
          </h2>
          <button
            onClick={() => setShowAddProduct(true)}
            className="btn-secondary text-sm"
          >
            <Plus className="w-4 h-4 mr-1" />
            Add Product
          </button>
        </div>
        <div className="card-body">
          {templateData?.products?.length > 0 ? (
            <div className="space-y-4">
              {templateData.products.map((product: any) => (
                <div
                  key={product.id}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span
                          className={cn(
                            'text-xs px-2 py-0.5 rounded font-medium',
                            getSupplierColor(product.supplier_type)
                          )}
                        >
                          {getSupplierName(product.supplier_type)}
                        </span>
                        <h3 className="font-medium text-gray-900">
                          {product.product_name}
                        </h3>
                      </div>
                      {product.alias_name && (
                        <p className="text-sm text-primary-600 mt-1 font-medium">
                          Alias: {product.alias_name}
                        </p>
                      )}
                      {product.product_type && (
                        <p className="text-sm text-gray-500 mt-1">
                          {product.product_type}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setShowPricing(showPricing === product.id ? null : product.id)}
                        className="text-primary-600 hover:text-primary-700"
                        title="View Pricing"
                      >
                        <DollarSign className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setEditingProduct(product.id)}
                        className="text-gray-600 hover:text-gray-700"
                        title="Edit Product"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Remove this product?')) {
                            deleteProductMutation.mutate(product.id)
                          }
                        }}
                        className="text-red-600 hover:text-red-700"
                        title="Remove Product"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Pricing View */}
                  {showPricing === product.id && product.selected_sizes?.length > 0 && product.colors?.length > 0 && (
                    <ProductPricing
                      templateId={Number(templateId)}
                      productId={product.id}
                      productName={product.product_name}
                      aliasName={product.alias_name}
                      sizes={product.selected_sizes}
                      colors={product.colors}
                    />
                  )}

                  {/* Sizes */}
                  {product.selected_sizes?.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs text-gray-500 mb-1">Sizes:</p>
                      <div className="flex flex-wrap gap-1">
                        {product.selected_sizes.map((size: string) => (
                          <span
                            key={size}
                            className="text-xs bg-gray-100 px-2 py-0.5 rounded"
                          >
                            {size}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Colors */}
                  <div className="mt-3">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-xs text-gray-500">Colors:</p>
                      <button
                        onClick={() => setShowAddColor(product.id)}
                        className="text-xs text-primary-600 hover:text-primary-700"
                      >
                        <Plus className="w-3 h-3 inline" /> Add Color
                      </button>
                    </div>
                    {product.colors?.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {product.colors.map((color: any) => (
                          <div
                            key={color.id}
                            className="flex items-center space-x-1 bg-gray-50 px-2 py-1 rounded"
                          >
                            {color.color_hex && (
                              <div
                                className="w-4 h-4 rounded-full border border-gray-300"
                                style={{ backgroundColor: color.color_hex }}
                              />
                            )}
                            <span className="text-sm">
                              {color.display_name || color.color_name}
                            </span>
                            <button
                              onClick={() =>
                                deleteColorMutation.mutate({
                                  productId: product.id,
                                  colorId: color.id,
                                })
                              }
                              className="text-gray-400 hover:text-red-600"
                            >
                              <X className="w-3 h-3" />
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-400">No colors added</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Package className="w-12 h-12 mx-auto text-gray-300" />
              <p className="mt-2 text-gray-500">No products added yet</p>
              <button
                onClick={() => setShowAddProduct(true)}
                className="mt-2 btn-secondary text-sm"
              >
                Add Your First Product
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Add Product Modal */}
      {showAddProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold">Add Product</h2>
              <button onClick={() => setShowAddProduct(false)}>
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form
              onSubmit={handleSubmit((data) => {
                const submitData: any = {
                  ...data,
                  selected_sizes: data.selected_sizes_string
                    ? data.selected_sizes_string.split(',').map((s: string) => s.trim())
                    : [],
                }
                delete submitData.selected_sizes_string
                addProductMutation.mutate(submitData)
              })}
            >
              <div className="p-6 space-y-4">
                <div>
                  <label className="label">Supplier *</label>
                  <select {...register('supplier_type')} className="input" required>
                    <option value="">Select supplier</option>
                    {connectedSuppliers.map((s: any) => (
                      <option key={s.supplier_type} value={s.supplier_type}>
                        {getSupplierName(s.supplier_type)}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Product Name *</label>
                  <input
                    {...register('product_name')}
                    type="text"
                    className="input"
                    required
                    placeholder="e.g., Gildan 18000 Sweatshirt"
                  />
                </div>
                <div>
                  <label className="label">Product Type</label>
                  <input
                    {...register('product_type')}
                    type="text"
                    className="input"
                    placeholder="e.g., Gildan 18000"
                  />
                </div>
                <div>
                  <label className="label">Alias Name (unique within template)</label>
                  <input
                    {...register('alias_name')}
                    type="text"
                    className="input"
                    placeholder="e.g., Premium Sweatshirt"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Optional: A unique name to identify this product in the template
                  </p>
                </div>
                <div>
                  <label className="label">Sizes (comma-separated)</label>
                  <input
                    {...register('selected_sizes_string')}
                    type="text"
                    className="input"
                    placeholder="S, M, L, XL, 2XL"
                  />
                </div>
                <div>
                  <label className="label">Pricing Mode</label>
                  <select {...register('pricing_mode')} className="input" defaultValue="global">
                    <option value="global">Global (same price for all)</option>
                    <option value="per_size">Per Size</option>
                    <option value="per_color">Per Color</option>
                    <option value="per_config">Per Configuration (Size + Color)</option>
                  </select>
                </div>
                <div>
                  <label className="label">Global Price</label>
                  <input
                    {...register('global_price', { valueAsNumber: true })}
                    type="number"
                    step="0.01"
                    className="input"
                    placeholder="29.99"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Default price (can be overridden per size/color/config)
                  </p>
                </div>
              </div>
              <div className="p-4 border-t flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowAddProduct(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addProductMutation.isPending}
                  className="flex-1 btn-primary"
                >
                  {addProductMutation.isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    'Add Product'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Color Modal */}
      {showAddColor && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-sm w-full">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-lg font-semibold">Add Color</h2>
              <button onClick={() => setShowAddColor(null)}>
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form
              onSubmit={handleSubmit((data) =>
                addColorMutation.mutate({ productId: showAddColor, data })
              )}
            >
              <div className="p-6 space-y-4">
                <div>
                  <label className="label">Color Name *</label>
                  <input
                    {...register('color_name')}
                    type="text"
                    className="input"
                    required
                    placeholder="e.g., Black"
                  />
                </div>
                <div>
                  <label className="label">Color Code (Hex)</label>
                  <input
                    {...register('color_hex')}
                    type="text"
                    className="input"
                    placeholder="#000000"
                  />
                </div>
                <div>
                  <label className="label">Display Name (optional)</label>
                  <input
                    {...register('display_name')}
                    type="text"
                    className="input"
                    placeholder="Custom display name"
                  />
                </div>
              </div>
              <div className="p-4 border-t flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowAddColor(null)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addColorMutation.isPending}
                  className="flex-1 btn-primary"
                >
                  Add Color
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {editingProduct && (() => {
        const product = templateData?.products?.find((p: any) => p.id === editingProduct)
        if (!product) return null

        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b sticky top-0 bg-white">
                <h2 className="text-xl font-semibold">Edit Product</h2>
                <button onClick={() => setEditingProduct(null)}>
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              <form
                onSubmit={handleSubmit((data) => {
                  const submitData: any = {
                    ...data,
                    selected_sizes: data.selected_sizes_string
                      ? data.selected_sizes_string.split(',').map((s: string) => s.trim())
                      : product.selected_sizes,
                  }
                  delete submitData.selected_sizes_string
                  updateProductMutation.mutate({ productId: editingProduct, data: submitData })
                })}
              >
                <div className="p-6 space-y-4">
                  <div>
                    <label className="label">Product Name *</label>
                    <input
                      {...register('product_name')}
                      type="text"
                      className="input"
                      defaultValue={product.product_name}
                      required
                    />
                  </div>
                  <div>
                    <label className="label">Alias Name</label>
                    <input
                      {...register('alias_name')}
                      type="text"
                      className="input"
                      defaultValue={product.alias_name}
                      placeholder="e.g., Premium Sweatshirt"
                    />
                    <p className="mt-1 text-xs text-gray-500">
                      Optional: A unique name to identify this product in the template
                    </p>
                  </div>
                  <div>
                    <label className="label">Sizes (comma-separated)</label>
                    <input
                      {...register('selected_sizes_string')}
                      type="text"
                      className="input"
                      defaultValue={product.selected_sizes?.join(', ')}
                      placeholder="S, M, L, XL, 2XL"
                    />
                  </div>
                  <div>
                    <label className="label">Pricing Mode</label>
                    <select
                      {...register('pricing_mode')}
                      className="input"
                      defaultValue={product.pricing_mode || 'global'}
                    >
                      <option value="global">Global (same price for all)</option>
                      <option value="per_size">Per Size</option>
                      <option value="per_color">Per Color</option>
                      <option value="per_config">Per Configuration (Size + Color)</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Global Price</label>
                    <input
                      {...register('global_price', {
                        valueAsNumber: true,
                      })}
                      type="number"
                      step="0.01"
                      className="input"
                      defaultValue={product.global_price}
                      placeholder="29.99"
                    />
                  </div>
                </div>
                <div className="p-4 border-t flex space-x-3 sticky bottom-0 bg-white">
                  <button
                    type="button"
                    onClick={() => setEditingProduct(null)}
                    className="flex-1 btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={updateProductMutation.isPending}
                    className="flex-1 btn-primary"
                  >
                    {updateProductMutation.isPending ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      'Save Changes'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )
      })()}

      {/* Create Listing Modal */}
      {showCreateListing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold">Create Listing</h2>
              <button onClick={() => setShowCreateListing(false)}>
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <form
              onSubmit={handleSubmit((data) => createListingMutation.mutate(data))}
            >
              <div className="p-6 space-y-4">
                <div>
                  <label className="label">Target Shop *</label>
                  <select {...register('shop_id')} className="input" required>
                    <option value="">Select shop</option>
                    {shopsList
                      .filter((s: any) => s.is_connected)
                      .map((shop: any) => (
                        <option key={shop.id} value={shop.id}>
                          {shop.shop_name} ({shop.shop_type})
                        </option>
                      ))}
                  </select>
                </div>
                <div>
                  <label className="label">Listing Title</label>
                  <input
                    {...register('title')}
                    type="text"
                    className="input"
                    placeholder={templateData?.default_title || 'Enter title'}
                  />
                </div>
                <div>
                  <label className="label">Price</label>
                  <input
                    {...register('price', { valueAsNumber: true })}
                    type="number"
                    step="0.01"
                    className="input"
                    placeholder="29.99"
                  />
                </div>
              </div>
              <div className="p-4 border-t flex space-x-3">
                <button
                  type="button"
                  onClick={() => setShowCreateListing(false)}
                  className="flex-1 btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createListingMutation.isPending}
                  className="flex-1 btn-primary"
                >
                  {createListingMutation.isPending ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    'Create Listing'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
