/**
 * Deployment verification page.
 * Fetches /api/health and displays backend version + frontend build info.
 * Used by E2E tests to confirm both frontend and backend are running.
 */
import { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || '/api'
const BUILD_ID = import.meta.env.VITE_BUILD_ID || 'local'

export default function Version() {
  const [health, setHealth] = useState<{ status?: string; version?: string } | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_BASE.replace(/\/$/, '')}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6" style={{ background: 'var(--t-bg, #f9fafb)' }}>
      <div className="card card-body max-w-md w-full">
        <h1 className="text-xl font-bold mb-4">Deployment check</h1>
        <div className="space-y-2 text-sm">
          <p data-testid="frontend-build">
            <strong>Frontend build:</strong> {BUILD_ID}
          </p>
          {error && (
            <p data-testid="backend-error" className="text-red-600">
              <strong>Backend:</strong> {error}
            </p>
          )}
          {health && (
            <>
              <p data-testid="backend-status">
                <strong>Backend status:</strong> {health.status}
              </p>
              <p data-testid="backend-version">
                <strong>Backend version:</strong> {health.version ?? '—'}
              </p>
            </>
          )}
        </div>
        {health?.status === 'healthy' && (
          <p className="mt-4 text-green-600 font-medium" data-testid="deployment-ok">
            Frontend and backend are running.
          </p>
        )}
      </div>
    </div>
  )
}
