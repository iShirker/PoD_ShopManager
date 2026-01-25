export type HelpDocMap = Record<string, string>

function basename(p: string) {
  const parts = p.split(/[\\/]/g)
  return parts[parts.length - 1] || p
}

/**
 * Load docs from repo-root `docs/pages/*.md` as raw strings.
 *
 * These files are authored as product/design docs and reused as in-app Help content.
 * Vite dev-server must be allowed to read the monorepo root (see `vite.config.ts`).
 */
const rawDocs = (import.meta.glob('../../../docs/pages/*.md', {
  as: 'raw',
  eager: true,
}) || {}) as Record<string, string>

export const helpDocsByFileName: HelpDocMap = Object.fromEntries(
  Object.entries(rawDocs).map(([path, content]) => [basename(path), content])
)

export function getHelpDocMarkdown(fileName?: string | null) {
  if (!fileName) return null
  return helpDocsByFileName[fileName] ?? null
}

