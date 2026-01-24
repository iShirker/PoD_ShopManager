import { useState } from 'react'
import { X, CreditCard, Wallet, Smartphone, Building2, Banknote, Globe } from 'lucide-react'
import { cn } from '../lib/utils'

type Region = 'usa' | 'europe' | 'other'

interface PaymentOption {
  id: string
  label: string
  description: string
  icon: React.ElementType
}

const REGIONS: { id: Region; label: string; icon: React.ElementType; options: PaymentOption[] }[] = [
  {
    id: 'usa',
    label: 'United States',
    icon: Building2,
    options: [
      { id: 'card_usa', label: 'Credit / Debit Card', description: 'Visa, Mastercard, Amex', icon: CreditCard },
      { id: 'paypal_usa', label: 'PayPal', description: 'Pay with your PayPal account', icon: Wallet },
      { id: 'apple_usa', label: 'Apple Pay', description: 'Quick and secure', icon: Smartphone },
    ],
  },
  {
    id: 'europe',
    label: 'Europe',
    icon: Building2,
    options: [
      { id: 'sepa', label: 'SEPA Direct Debit', description: 'Euro bank transfer', icon: Banknote },
      { id: 'ideal', label: 'iDEAL', description: 'Netherlands', icon: CreditCard },
      { id: 'klarna', label: 'Klarna', description: 'Pay later or in installments', icon: Wallet },
    ],
  },
  {
    id: 'other',
    label: 'Other regions',
    icon: Globe,
    options: [
      { id: 'card_other', label: 'Credit / Debit Card', description: 'Visa, Mastercard', icon: CreditCard },
      { id: 'paypal_other', label: 'PayPal', description: 'Pay with your PayPal account', icon: Wallet },
      { id: 'google_other', label: 'Google Pay', description: 'Quick and secure', icon: Smartphone },
    ],
  },
]

interface PaymentModalProps {
  open: boolean
  onClose: () => void
  total: number
  currency: string
  planName: string
  interval: 'monthly' | 'yearly'
}

export default function PaymentModal({ open, onClose, total, currency, planName, interval }: PaymentModalProps) {
  const [region, setRegion] = useState<Region>('usa')
  const [selected, setSelected] = useState<string | null>(null)

  if (!open) return null

  const regionConfig = REGIONS.find((r) => r.id === region)!

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} aria-hidden="true" />
      <div
        className="relative card w-full max-w-lg max-h-[90vh] overflow-y-auto"
        style={{ background: 'var(--t-card-bg)', borderColor: 'var(--t-card-border)' }}
        role="dialog"
        aria-modal="true"
        aria-labelledby="payment-modal-title"
      >
        <div className="sticky top-0 flex items-center justify-between p-4 border-b shrink-0" style={{ borderColor: 'var(--t-card-border)', background: 'var(--t-card-bg)' }}>
          <h2 id="payment-modal-title" className="section-title" style={{ color: 'var(--t-main-text)' }}>
            Complete payment
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-black/5 transition-colors"
            style={{ color: 'var(--t-muted)' }}
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div className="flex flex-wrap gap-2">
            {REGIONS.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => { setRegion(r.id); setSelected(null) }}
                className={cn(
                  'inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
                  region === r.id ? 'opacity-100' : 'opacity-60 hover:opacity-80'
                )}
                style={{
                  background: region === r.id ? 'var(--t-sidebar-active-bg)' : 'var(--t-card-border)',
                  color: region === r.id ? 'var(--t-accent)' : 'var(--t-muted)',
                }}
              >
                <r.icon className="w-4 h-4" />
                {r.label}
              </button>
            ))}
          </div>

          <p className="text-sm" style={{ color: 'var(--t-muted)' }}>
            {planName} · {interval === 'yearly' ? 'Yearly' : 'Monthly'}
          </p>

          <div className="space-y-2">
            {regionConfig.options.map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setSelected(opt.id)}
                className={cn(
                  'w-full flex items-center gap-4 p-4 rounded-xl border-2 text-left transition-colors',
                  selected === opt.id ? 'border-[var(--t-accent)]' : ''
                )}
                style={{
                  borderColor: selected === opt.id ? 'var(--t-accent)' : 'var(--t-card-border)',
                  background: selected === opt.id ? 'var(--t-sidebar-active-bg)' : 'transparent',
                }}
              >
                <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{ background: 'var(--t-sidebar-active-bg)' }}>
                  <opt.icon className="w-6 h-6" style={{ color: 'var(--t-accent)' }} />
                </div>
                <div>
                  <p className="font-semibold body-text" style={{ color: 'var(--t-main-text)' }}>{opt.label}</p>
                  <p className="text-sm text-muted">{opt.description}</p>
                </div>
              </button>
            ))}
          </div>

          <p className="text-xs" style={{ color: 'var(--t-muted)' }}>
            Payment processing is not yet connected. This is a placeholder UI.
          </p>
        </div>

        <div className="sticky bottom-0 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4 p-4 border-t" style={{ borderColor: 'var(--t-card-border)', background: 'var(--t-card-bg)' }}>
          <div>
            <p className="text-sm text-muted">Total due</p>
            <p className="text-2xl font-bold" style={{ color: 'var(--t-accent)' }}>
              {currency} {total.toFixed(2)}
            </p>
          </div>
          <div className="flex gap-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1 sm:flex-none">
              Cancel
            </button>
            <button
              type="button"
              className="btn-primary flex-1 sm:flex-none"
              disabled={!selected}
            >
              Pay {currency} {total.toFixed(2)}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
