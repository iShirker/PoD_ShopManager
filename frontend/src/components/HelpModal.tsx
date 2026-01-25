import { useEffect } from 'react'
import { X } from 'lucide-react'
import type { HelpEntry } from '../help/helpRegistry'
import { getHelpDocMarkdown } from '../help/helpDocs'

type Props = {
  open: boolean
  onClose: () => void
  help: HelpEntry
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="text-sm font-semibold uppercase tracking-wider text-muted mb-2">{children}</h3>
}

export default function HelpModal({ open, onClose, help }: Props) {
  const doc = getHelpDocMarkdown(help.docFile)

  useEffect(() => {
    if (!open) return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  useEffect(() => {
    if (!open) return
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = prev
    }
  }, [open])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50">
      <button
        type="button"
        aria-label="Close help"
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      <div className="absolute inset-0 flex items-start justify-center p-4 sm:p-6">
        <div className="card w-full max-w-3xl max-h-[85vh] overflow-hidden">
          <div className="card-header flex items-center justify-between">
            <div className="min-w-0">
              <div className="text-xs text-muted">Help</div>
              <div className="text-lg font-semibold truncate">{help.title}</div>
              <div className="text-xs text-muted truncate">Route: {help.route}</div>
            </div>
            <button type="button" className="btn-secondary px-3 py-2" onClick={onClose} aria-label="Close">
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="card-body overflow-y-auto space-y-6">
            <section>
              <SectionTitle>Designed for</SectionTitle>
              <p className="body-text">{help.designedFor}</p>
            </section>

            <section className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <SectionTitle>Features</SectionTitle>
                <ul className="list-disc pl-5 space-y-1">
                  {help.features.map((f) => (
                    <li key={f} className="body-text">
                      {f}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <SectionTitle>Objects</SectionTitle>
                <ul className="list-disc pl-5 space-y-1">
                  {help.objects.map((o) => (
                    <li key={o} className="body-text">
                      {o}
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            <section>
              <SectionTitle>How to use this screen</SectionTitle>
              <div className="space-y-4">
                {help.instructions.map((block) => (
                  <div key={block.title} className="card p-4">
                    <div className="font-semibold mb-2">{block.title}</div>
                    <ol className="list-decimal pl-5 space-y-1">
                      {block.steps.map((s) => (
                        <li key={s} className="body-text">
                          {s}
                        </li>
                      ))}
                    </ol>
                  </div>
                ))}
              </div>
            </section>

            {doc && (
              <section>
                <SectionTitle>More details (design doc)</SectionTitle>
                <div className="card p-4">
                  <pre className="whitespace-pre-wrap text-sm leading-6">
                    {doc}
                  </pre>
                </div>
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

