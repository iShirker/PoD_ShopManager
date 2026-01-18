import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function formatDateTime(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function getSupplierColor(supplier: string): string {
  const colors: Record<string, string> = {
    gelato: 'bg-purple-100 text-purple-800',
    printify: 'bg-green-100 text-green-800',
    printful: 'bg-blue-100 text-blue-800',
  }
  return colors[supplier] || 'bg-gray-100 text-gray-800'
}

export function getSupplierName(supplier: string): string {
  const names: Record<string, string> = {
    gelato: 'Gelato',
    printify: 'Printify',
    printful: 'Printful',
  }
  return names[supplier] || supplier
}

export function getShopTypeColor(shopType: string): string {
  const colors: Record<string, string> = {
    etsy: 'bg-orange-100 text-orange-800',
    shopify: 'bg-green-100 text-green-800',
  }
  return colors[shopType] || 'bg-gray-100 text-gray-800'
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}
