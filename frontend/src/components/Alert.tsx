import type { ReactNode } from 'react'

interface AlertProps {
  variant: 'error' | 'success' | 'info'
  children: ReactNode
  onRetry?: () => void
}

export default function Alert({ variant, children, onRetry }: AlertProps) {
  return (
    <div className={`alert alert-${variant}`} role="alert">
      <p>{children}</p>
      {onRetry && (
        <button type="button" className="btn btn-secondary btn-sm" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  )
}
