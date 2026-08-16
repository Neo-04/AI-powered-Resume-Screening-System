import type { ParsedResume } from '../types/api'

interface ParsedResumeCardProps {
  data: ParsedResume
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

export default function ParsedResumeCard({ data }: ParsedResumeCardProps) {
  return (
    <div className="result-card">
      <h3>Parsed Resume</h3>
      <dl className="detail-grid">
        {data.name && (
          <>
            <dt>Name</dt>
            <dd>{data.name}</dd>
          </>
        )}
        {data.degree && (
          <>
            <dt>Degree</dt>
            <dd>{data.degree}</dd>
          </>
        )}
        {data.branch && (
          <>
            <dt>Branch</dt>
            <dd>{data.branch}</dd>
          </>
        )}
        <dt>Experience (years)</dt>
        <dd>{data.experience_years}</dd>
      </dl>
      <TagList title="Skills" items={data.skills} />
      <TagList title="Education" items={data.education} />
      <TagList title="Experience" items={data.experience} />
      <TagList title="Projects" items={data.projects} />
      <TagList title="Achievements" items={data.achievements} />
    </div>
  )
}
