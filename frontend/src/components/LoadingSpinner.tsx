interface LoadingSpinnerProps {
  label?: string
}

export default function LoadingSpinner({
  label = 'Loading',
}: LoadingSpinnerProps) {
  return (
    <div className="loading-row" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}…</span>
    </div>
  )
}
