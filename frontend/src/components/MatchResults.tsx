import type { MatchResult } from '../types/api'

interface MatchResultsProps {
  data: MatchResult
}

function scoreTone(score: number): string {
  if (score >= 75) return 'good'
  if (score >= 50) return 'medium'
  return 'low'
}

function TagList({
  title,
  items,
  variant,
}: {
  title: string
  items: string[]
  variant?: 'matched' | 'missing' | 'extra'
}) {
  return (
    <div className="detail-block">
      <h4>{title}</h4>
      {items.length === 0 ? (
        <p className="empty-note">None</p>
      ) : (
        <ul className={`tag-list ${variant ? `tag-list-${variant}` : ''}`}>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function MatchResults({ data }: MatchResultsProps) {
  const tone = scoreTone(data.match_score)

  return (
    <section className="match-results" aria-labelledby="match-results-heading">
      <div className="match-header">
        <div>
          <h2 id="match-results-heading">Matching Results</h2>
          {data.recommendation && (
            <p className="recommendation">{data.recommendation}</p>
          )}
        </div>
        <div className={`score-circle score-${tone}`} aria-label={`Overall match score ${data.match_score} out of 100`}>
          <span className="score-value">{data.match_score}</span>
          <span className="score-label">/ 100</span>
        </div>
      </div>

      <div className="score-breakdown">
        <div className="score-item">
          <span className="score-item-label">Skill Score</span>
          <span className="score-item-value">{data.skill_score}</span>
        </div>
        <div className="score-item">
          <span className="score-item-label">Experience Score</span>
          <span className="score-item-value">{data.experience_score}</span>
        </div>
        <div className="score-item">
          <span className="score-item-label">Qualification Score</span>
          <span className="score-item-value">{data.qualification_score}</span>
        </div>
        <div className="score-item">
          <span className="score-item-label">Soft Skill Score</span>
          <span className="score-item-value">{data.soft_skill_score}</span>
        </div>
      </div>

      <dl className="detail-grid match-flags">
        <dt>Experience Match</dt>
        <dd>{data.experience_match ? 'Yes' : 'No'}</dd>
        <dt>Qualification Match</dt>
        <dd>{data.qualification_match ? 'Yes' : 'No'}</dd>
      </dl>

      {data.matching_reason && (
        <div className="detail-block">
          <h4>Qualification Explanation</h4>
          <p>{data.matching_reason}</p>
        </div>
      )}

      <TagList title="Matched Skills" items={data.matched_skills} variant="matched" />
      <TagList title="Missing Skills" items={data.missing_skills} variant="missing" />
      <TagList title="Additional Skills" items={data.additional_skills} variant="extra" />
      <TagList title="Matched Keywords" items={data.matched_keywords} variant="matched" />
    </section>
  )
}
