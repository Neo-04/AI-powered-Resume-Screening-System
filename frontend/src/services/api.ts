import type {
  ApiErrorDetail,
  HealthResponse,
  JobDescription,
  MatchRequest,
  MatchResult,
  ParsedJD,
  ParsedResume,
  ResumeUploadResponse,
} from '../types/api'
import { ApiError, formatApiErrorDetail } from '../utils/errors'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)

  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    })
  } catch {
    throw new ApiError(
      'Unable to reach the server. Is the backend running?',
      0,
    )
  }

  if (response.ok) {
    if (response.status === 204) {
      return undefined as T
    }
    return (await response.json()) as T
  }

  let detail: ApiErrorDetail = 'Request failed.'
  try {
    const payload = (await response.json()) as { detail?: ApiErrorDetail }
    if (payload.detail !== undefined) {
      detail = payload.detail
    }
  } catch {
    detail = response.statusText || 'Request failed.'
  }

  throw new ApiError(formatApiErrorDetail(detail), response.status)
}

export function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/health')
}

export function uploadResume(file: File): Promise<ResumeUploadResponse> {
  const formData = new FormData()
  formData.append('file', file)
  return request<ResumeUploadResponse>('/upload-resume', {
    method: 'POST',
    body: formData,
  })
}

export function uploadJobDescriptionFile(
  file: File,
): Promise<JobDescription> {
  const formData = new FormData()
  formData.append('file', file)
  return request<JobDescription>('/upload-jd', {
    method: 'POST',
    body: formData,
  })
}

export function uploadJobDescriptionText(
  text: string,
): Promise<JobDescription> {
  const formData = new FormData()
  formData.append('text', text)
  return request<JobDescription>('/upload-jd', {
    method: 'POST',
    body: formData,
  })
}

export function parseResume(resumeId: string): Promise<ParsedResume> {
  return request<ParsedResume>(`/parse-resume/${resumeId}`, {
    method: 'POST',
  })
}

export function parseJobDescription(jdId: string): Promise<ParsedJD> {
  return request<ParsedJD>(`/parse-jd/${jdId}`, {
    method: 'POST',
  })
}

export function runMatch(payload: MatchRequest): Promise<MatchResult> {
  return request<MatchResult>('/match', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
