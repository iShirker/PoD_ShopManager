import { useState } from 'react'
import { Download, Upload, FileSpreadsheet } from 'lucide-react'

const CSV_TEMPLATE = `title,description,tags,variants
"Example Product","Example description","tag1, tag2, tag3","S, M, L"
`

export default function ListingsBulk() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string[][] | null>(null)
  const [creating, setCreating] = useState(false)
  const [result, setResult] = useState<{ ok: number; err: number } | null>(null)

  const handleDownloadTemplate = () => {
    const blob = new Blob([CSV_TEMPLATE], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'listings_template.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    setResult(null)
    const r = new FileReader()
    r.onload = () => {
      const text = (r.result as string) || ''
      const rows = text.split(/\r?\n/).filter(Boolean).map((row) => row.split(',').map((c) => c.replace(/^"|"$/g, '').trim()))
      setPreview(rows.slice(0, 6))
    }
    r.readAsText(f)
  }

  const handleCreate = async () => {
    if (!file) return
    setCreating(true)
    setResult(null)
    try {
      // Placeholder: simulate bulk create
      await new Promise((r) => setTimeout(r, 800))
      setResult({ ok: preview?.length ?? 0, err: 0 })
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="space-y-6" data-testid="listings-bulk">
      <div>
        <h1 className="page-title" style={{ color: 'var(--t-main-text)' }} data-testid="listings-bulk-title">
          Bulk Create
        </h1>
        <p className="text-muted mt-1 body-text">
          CSV import, template-based bulk listing creation
        </p>
      </div>

      <div className="card card-body space-y-6">
        <div className="flex flex-wrap gap-4 items-center">
          <a
            href="#"
            onClick={(e) => { e.preventDefault(); handleDownloadTemplate(); }}
            className="inline-flex items-center gap-2 btn-secondary"
            data-testid="listings-bulk-download-template"
          >
            <Download className="w-5 h-5" />
            Download template
          </a>
          <label className="inline-flex items-center gap-2 btn-primary cursor-pointer">
            <Upload className="w-5 h-5" />
            <span>Upload CSV</span>
            <input
              type="file"
              accept=".csv"
              className="sr-only"
              onChange={handleFileChange}
              data-testid="listings-bulk-upload"
            />
          </label>
        </div>

        {file && (
          <>
            <p className="text-sm text-muted" data-testid="listings-bulk-file-name">
              File: {file.name}
            </p>
            {preview && preview.length > 0 && (
              <div className="overflow-x-auto">
                <table className="w-full text-sm border-collapse" data-testid="listings-bulk-preview">
                  <thead>
                    <tr className="border-b">
                      {preview[0].map((h, i) => (
                        <th key={i} className="text-left py-2 px-2 font-medium">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.slice(1).map((row, i) => (
                      <tr key={i} className="border-b">
                        {row.map((c, j) => (
                          <td key={j} className="py-2 px-2">{c}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="text-xs text-muted mt-2">Preview (first 5 data rows)</p>
              </div>
            )}
            <button
              onClick={handleCreate}
              disabled={creating}
              className="btn-primary"
              data-testid="listings-bulk-create"
            >
              {creating ? 'Creating…' : 'Create listings'}
            </button>
          </>
        )}

        {!file && (
          <div className="flex flex-col items-center justify-center py-12 text-muted">
            <FileSpreadsheet className="w-16 h-16 mb-4 opacity-50" />
            <p>Upload a CSV to preview and create listings.</p>
          </div>
        )}

        {result && (
          <div className="p-4 rounded-lg bg-green-50 border border-green-200 text-green-800" data-testid="listings-bulk-result">
            Created {result.ok} listing(s). {result.err > 0 ? `${result.err} error(s).` : ''}
          </div>
        )}
      </div>
    </div>
  )
}
