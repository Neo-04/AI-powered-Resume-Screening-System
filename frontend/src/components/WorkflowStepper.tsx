interface WorkflowStepperProps {
  resumeUploaded: boolean
  resumeParsed: boolean
  jdUploaded: boolean
  jdParsed: boolean
  matchComplete: boolean
}

const STEPS = [
  { key: 'upload-resume', label: 'Upload Resume' },
  { key: 'parse-resume', label: 'Parse Resume' },
  { key: 'upload-jd', label: 'Upload Job Description' },
  { key: 'parse-jd', label: 'Parse Job Description' },
  { key: 'match', label: 'Run Matching' },
  { key: 'results', label: 'View Results' },
] as const

export default function WorkflowStepper({
  resumeUploaded,
  resumeParsed,
  jdUploaded,
  jdParsed,
  matchComplete,
}: WorkflowStepperProps) {
  const completed = [
    resumeUploaded,
    resumeParsed,
    jdUploaded,
    jdParsed,
    matchComplete,
    matchComplete,
  ]

  const activeIndex = completed.findIndex((step) => !step)

  return (
    <nav className="workflow-stepper" aria-label="Screening workflow progress">
      <ol>
        {STEPS.map((step, index) => {
          const isComplete = completed[index]
          const isActive = activeIndex === index
          const state = isComplete ? 'complete' : isActive ? 'active' : 'pending'

          return (
            <li key={step.key} className={`step step-${state}`}>
              <span className="step-marker" aria-hidden="true">
                {isComplete ? '✓' : index + 1}
              </span>
              <span className="step-label">{step.label}</span>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
