import { useState, useRef } from 'react'
import { Image, Upload, Download } from 'lucide-react'

const MOCK_PRODUCTS = [
  { id: '1', name: 'Unisex Staple T-Shirt' },
  { id: '2', name: 'Classic Hoodie' },
  { id: '3', name: 'Poster 18x24' },
]

export default function Mockups() {
  const [product, setProduct] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    const url = URL.createObjectURL(f)
    setPreviewUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev)
      return url
    })
  }

  const handleDownload = () => {
    if (!previewUrl) return
    const a = document.createElement('a')
    a.href = previewUrl
    a.download = file?.name || 'mockup.png'
    a.click()
  }

  return (
    <div className="space-y-6" data-testid="mockups">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="mockups-title">
          Mockup Studio
        </h1>
        <p className="text-muted mt-1 body-text">
          Create preview and production mockups
        </p>
      </div>

      <div className="card card-body space-y-6">
        <div>
          <label className="label">Product</label>
          <select
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            className="input max-w-xs"
            data-testid="mockups-product-select"
          >
            <option value="">Select product</option>
            {MOCK_PRODUCTS.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">Design</label>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            className="sr-only"
            onChange={handleFileChange}
            data-testid="mockups-upload"
          />
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <Upload className="w-5 h-5" />
            Upload design
          </button>
        </div>

        {previewUrl && (
          <div data-testid="mockups-preview">
            <p className="label mb-2">Preview</p>
            <div className="border rounded-lg p-4 inline-block" style={{ borderColor: 'var(--t-card-border)' }}>
              <img src={previewUrl} alt="Preview" className="max-w-xs max-h-64 object-contain" />
            </div>
            <div className="mt-4">
              <button
                type="button"
                onClick={handleDownload}
                className="btn-primary inline-flex items-center gap-2"
                data-testid="mockups-download"
              >
                <Download className="w-5 h-5" />
                Download
              </button>
            </div>
          </div>
        )}

        {!previewUrl && (
          <div className="flex flex-col items-center justify-center py-12 text-muted">
            <Image className="w-16 h-16 mb-4 opacity-50" />
            <p>Select a product and upload a design to generate a mockup.</p>
          </div>
        )}
      </div>
    </div>
  )
}
