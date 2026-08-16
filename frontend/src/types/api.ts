export interface ResumeUploadResponse {
  resume_id: string
  filename: string
  char_count: number
  text: string
}

export interface ParsedResume {
  resume_id: string
  name: string
  skills: string[]
  education: string[]
  experience: string[]
  projects: string[]
  achievements: string[]
  degree: string
  branch: string
  experience_years: number
}

export interface JobDescription {
  jd_id: string
  filename: string
  char_count: number
  text: string
}

export interface ParsedJD {
  jd_id: string
  role: string
  required_skills: string[]
  preferred_qualification: string[]
  experience: string
  keywords: string[]
}

export interface MatchRequest {
  resume_id: string
  jd_id: string
}

export interface MatchResult {
  match_score: number
  skill_score: number
  experience_score: number
  qualification_score: number
  soft_skill_score: number
  matched_skills: string[]
  missing_skills: string[]
  additional_skills: string[]
  qualification_match: boolean
  matching_reason: string
  experience_match: boolean
  matched_keywords: string[]
  recommendation: string
}

export interface HealthResponse {
  status: string
}

export interface ValidationErrorItem {
  loc: (string | number)[]
  msg: string
  type: string
}

export type ApiErrorDetail = string | ValidationErrorItem[]
