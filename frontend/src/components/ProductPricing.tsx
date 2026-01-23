import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { templatesApi } from '../lib/api'
import { Loader2 } from 'lucide-react'
import { cn } from '../lib/utils'

interface ProductPricingProps {
  templateId: number
  productId: number
  productName: string
  aliasName?: string
  sizes: string[]
  colors: Array<{ id: number; color_name: string; color_hex?: string; display_name?: string }>
}

type ViewMode = 'config' | 'size' | 'color'

export default function ProductPricing({
  templateId,
  productId,
  productName,
  aliasName,
}: ProductPricingProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('config')

  const { data: pricing, isLoading } = useQuery({
    queryKey: ['template-product-pricing', templateId, productId, viewMode],
    queryFn: () => templatesApi.getProductPricing(templateId, productId, viewMode),
    enabled: !!templateId && !!productId,
  })

  const pricingData = pricing?.data

  if (isLoading) {
    return (
      <div className="flex justify-center py-4">
        <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
      </div>
    )
  }

  if (!pricingData) {
    return (
      <div className="text-sm text-gray-500 py-4">
        No pricing data available. Make sure the product has sizes and colors configured.
      </div>
    )
  }

  return (
    <div className="mt-4 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-medium text-gray-900">
            {aliasName || productName}
          </h4>
          <p className="text-xs text-gray-500 mt-1">
            Cost: ${pricingData.total_cost?.toFixed(2)} (Base: ${pricingData.base_cost?.toFixed(2)} + Shipping: ${pricingData.shipping_cost?.toFixed(2)})
          </p>
        </div>
        <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('config')}
            className={cn(
              'px-3 py-1 text-xs font-medium rounded transition-colors',
              viewMode === 'config'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            By Config
          </button>
          <button
            onClick={() => setViewMode('size')}
            className={cn(
              'px-3 py-1 text-xs font-medium rounded transition-colors',
              viewMode === 'size'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            By Size
          </button>
          <button
            onClick={() => setViewMode('color')}
            className={cn(
              'px-3 py-1 text-xs font-medium rounded transition-colors',
              viewMode === 'color'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            )}
          >
            By Color
          </button>
        </div>
      </div>

      {viewMode === 'config' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-medium text-gray-700">Size</th>
                <th className="text-left py-2 px-3 font-medium text-gray-700">Color</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Cost</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Price</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Profit</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Margin</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(pricingData.data || {}).map(([key, item]: [string, any]) => (
                <tr key={key} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-2 px-3">{item.size}</td>
                  <td className="py-2 px-3">
                    <div className="flex items-center space-x-2">
                      {item.color_hex && (
                        <div
                          className="w-4 h-4 rounded-full border border-gray-300"
                          style={{ backgroundColor: item.color_hex }}
                        />
                      )}
                      <span>{item.color}</span>
                    </div>
                  </td>
                  <td className="py-2 px-3 text-right font-mono">${item.cost?.toFixed(2)}</td>
                  <td className="py-2 px-3 text-right font-mono">${item.price?.toFixed(2)}</td>
                  <td className={cn(
                    'py-2 px-3 text-right font-mono font-medium',
                    item.profit >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    ${item.profit?.toFixed(2)}
                  </td>
                  <td className={cn(
                    'py-2 px-3 text-right font-mono text-xs',
                    item.profit_margin >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {item.profit_margin?.toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {viewMode === 'size' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-medium text-gray-700">Size</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Cost</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Avg Price</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Avg Profit</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Margin</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Configs</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(pricingData.data || {}).map(([size, item]: [string, any]) => (
                <tr key={size} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-2 px-3 font-medium">{item.size}</td>
                  <td className="py-2 px-3 text-right font-mono">${item.cost?.toFixed(2)}</td>
                  <td className="py-2 px-3 text-right font-mono">${item.price?.toFixed(2)}</td>
                  <td className={cn(
                    'py-2 px-3 text-right font-mono font-medium',
                    item.profit >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    ${item.profit?.toFixed(2)}
                  </td>
                  <td className={cn(
                    'py-2 px-3 text-right font-mono text-xs',
                    item.profit_margin >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {item.profit_margin?.toFixed(1)}%
                  </td>
                  <td className="py-2 px-3 text-right text-gray-500">{item.config_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {viewMode === 'color' && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3 font-medium text-gray-700">Color</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Cost</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Avg Price</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Avg Profit</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Margin</th>
                <th className="text-right py-2 px-3 font-medium text-gray-700">Configs</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(pricingData.data || {}).map(([colorName, item]: [string, any]) => (
                <tr key={colorName} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-2 px-3">
                    <div className="flex items-center space-x-2">
                      {item.color_hex && (
                        <div
                          className="w-4 h-4 rounded-full border border-gray-300"
                          style={{ backgroundColor: item.color_hex }}
                        />
                      )}
                      <span className="font-medium">{item.color}</span>
                    </div>
                  </td>
                  <td className="py-2 px-3 text-right font-mono">${item.cost?.toFixed(2)}</td>
                  <td className="py-2 px-3 text-right font-mono">${item.price?.toFixed(2)}</td>
                  <td className={cn(
                    'py-2 px-3 text-right font-mono font-medium',
                    item.profit >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    ${item.profit?.toFixed(2)}
                  </td>
                  <td className={cn(
                    'py-2 px-3 text-right font-mono text-xs',
                    item.profit_margin >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {item.profit_margin?.toFixed(1)}%
                  </td>
                  <td className="py-2 px-3 text-right text-gray-500">{item.config_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
