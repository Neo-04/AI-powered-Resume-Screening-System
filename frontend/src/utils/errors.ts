import type { ApiErrorDetail } from '../types/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export function formatApiErrorDetail(detail: ApiErrorDetail): string {
  if (typeof detail === 'string') {
    return detail
  }

  return detail
    .map((item) => {
      const field = item.loc.filter((part) => part !== 'body').join('.')
      return field ? `${field}: ${item.msg}` : item.msg
    })
    .join('; ')
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message
  }

  if (error instanceof TypeError && error.message.includes('fetch')) {
    return 'Network error. Check your connection and try again.'
  }

  if (error instanceof Error) {
    return error.message
  }

  return 'An unexpected error occurred.'
}
