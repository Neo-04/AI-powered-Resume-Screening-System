import { useCallback, useEffect, useState } from 'react'
import type { HistoryJD, HistoryMatch, HistoryResume } from '../types/api'
import {
  fetchHistoryResumes,
  fetchHistoryJDs,
  fetchHistoryMatches,
} from '../services/api'

type HistoryTab = 'resumes' | 'jds' | 'matches'

function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function scoreBadgeClass(score: number | null): string {
  if (score === null) return ''
  if (score >= 75) return 'badge-good'
  if (score >= 50) return 'badge-medium'
  return 'badge-low'
}

export default function HistoryPanel() {
  const [tab, setTab] = useState<HistoryTab>('resumes')
  const [resumes, setResumes] = useState<HistoryResume[]>([])
  const [jds, setJDs] = useState<HistoryJD[]>([])
  const [matches, setMatches] = useState<HistoryMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async (activeTab: HistoryTab) => {
    setLoading(true)
    setError(null)
    try {
      if (activeTab === 'resumes') setResumes(await fetchHistoryResumes())
      else if (activeTab === 'jds') setJDs(await fetchHistoryJDs())
      else setMatches(await fetchHistoryMatches())
    } catch {
      setError('Failed to load history.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load(tab)
  }, [tab, load])

  return (
    <section className="panel history-panel" aria-labelledby="history-heading">
      <div className="history-header">
        <h2 id="history-heading">History</h2>
        <button
          type="button"
          className="btn btn-ghost btn-sm"
          onClick={() => void load(tab)}
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      <div className="tab-row" role="tablist" aria-label="History tabs">
        {(['resumes', 'jds', 'matches'] as HistoryTab[]).map((t) => (
          <button
            key={t}
            type="button"
            role="tab"
            aria-selected={tab === t}
            className={tab === t ? 'tab active' : 'tab'}
            onClick={() => setTab(t)}
          >
            {t === 'resumes' ? 'Resumes' : t === 'jds' ? 'Job Descriptions' : 'Matches'}
          </button>
        ))}
      </div>

      {loading && <p className="empty-note">Loading…</p>}
      {error && <p className="empty-note" style={{ color: 'var(--error)' }}>{error}</p>}

      {!loading && !error && tab === 'resumes' && (
        resumes.length === 0 ? (
          <p className="empty-note">No resumes uploaded yet.</p>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Uploaded</th>
                  <th>ID</th>
                </tr>
              </thead>
              <tbody>
                {resumes.map((r) => (
                  <tr key={r.id}>
                    <td>{r.original_filename}</td>
                    <td>{formatDate(r.created_at)}</td>
                    <td className="id-cell" title={r.id}>{r.id.slice(0, 8)}…</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {!loading && !error && tab === 'jds' && (
        jds.length === 0 ? (
          <p className="empty-note">No job descriptions uploaded yet.</p>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Title / Filename</th>
                  <th>Uploaded</th>
                  <th>ID</th>
                </tr>
              </thead>
              <tbody>
                {jds.map((j) => (
                  <tr key={j.id}>
                    <td>{j.title || j.original_filename || '—'}</td>
                    <td>{formatDate(j.created_at)}</td>
                    <td className="id-cell" title={j.id}>{j.id.slice(0, 8)}…</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}

      {!loading && !error && tab === 'matches' && (
        matches.length === 0 ? (
          <p className="empty-note">No match results yet.</p>
        ) : (
          <div className="history-table-wrap">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Overall</th>
                  <th>Skill</th>
                  <th>Exp</th>
                  <th>Qual</th>
                  <th>Soft</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {matches.map((m) => (
                  <tr key={m.id}>
                    <td>
                      <span className={`score-badge ${scoreBadgeClass(m.overall_score)}`}>
                        {m.overall_score ?? '—'}
                      </span>
                    </td>
                    <td>{m.skill_score ?? '—'}</td>
                    <td>{m.experience_score ?? '—'}</td>
                    <td>{m.qualification_score ?? '—'}</td>
                    <td>{m.soft_skill_score ?? '—'}</td>
                    <td>{formatDate(m.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      )}
    </section>
  )
}
