import type { ParsedJD } from '../types/api'

interface ParsedJdCardProps {
  data: ParsedJD
}

function TagList({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null

  return (
    <div className="detail-block">
      <h4>{title}</h4>
      <ul className="tag-list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

export default function ParsedJdCard({ data }: ParsedJdCardProps) {
  return (
    <div className="result-card">
      <h3>Parsed Job Description</h3>
      <dl className="detail-grid">
        {data.role && (
          <>
            <dt>Role</dt>
            <dd>{data.role}</dd>
          </>
        )}
        {data.experience && (
          <>
            <dt>Experience Required</dt>
            <dd>{data.experience}</dd>
          </>
        )}
      </dl>
      <TagList title="Required Skills" items={data.required_skills} />
      <TagList title="Preferred Qualifications" items={data.preferred_qualification} />
      <TagList title="Keywords" items={data.keywords} />
    </div>
  )
}
